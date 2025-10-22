import os
import json
import asyncio
import websockets
from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse, HTMLResponse
from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream, Gather
from app.utils.decorators_twilio_auth import validate_twilio_request
from app.utils.training_data_loader import get_cached_training_data
import openai


from app.utils.speech_services import synthesize_speech
from pathlib import Path
from fastapi.routing import APIRouter
from app.utils.db import fetch_available_slots
from app.utils.booking import build_context_text, parse_booking_intent, book_if_possible

# Initialize FastAPI app
voice_router = APIRouter()
# Set OpenAI API key
openai.api_key = os.environ.get('OPENAI_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
SYSTEM_MESSAGE = "You are a helpful dental receptionist. Use the availability to schedule appointments for patients. Ask clarifying questions if needed."
VOICE = "alloy"
PORT = int(os.getenv("PORT", 5050))

# Helper function to get AI response
async def get_ai_response(user_input):
    try:
        training_data = await get_cached_training_data()

        # Prepare the conversation history as a prompt
        conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in training_data])
        conversation_history += f"\nuser: {user_input}\nsystem:"

        response = openai.chat.completions.create(
            model="gpt-4",
            messages = [{"role": "system", "content": "You are an AI assistant for an insurance company."},
                        {"role": "user", "content": user_input}]
        )

        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(e)
        return e.message

# Twilio voice route (main entry)
#@voice_router.post("/voice")
@voice_router.post("/incoming-call")
@validate_twilio_request
async def voice(request: Request):
    """
    Twilio will call this webhook when a call arrives.
    We'll return TwiML to instruct Twilio to stream media to our /media-stream WS endpoint.
    """
    host = request.url.hostname
    vr = VoiceResponse()

    vr.say("Welcome to the dental office. Please wait while we connect you to our AI assistant.", voice=VOICE)
    connect = Connect()

    connect.stream(url=f"wss://{host}/media-stream")
    vr.append(connect)

    return HTMLResponse(content=str(vr), media_type="application/xml")

@voice_router.websocket("/media-stream")
async def media_stream(ws: WebSocket):
    """
    WebSocket endpoint Twilio will send media to.
    We’ll also connect to OpenAI Realtime and proxy audio both ways.
    We’ll insert booking logic by interjecting system/context messages if needed.
    """
    await ws.accept()
    openai_ws = await websockets.connect(
        "wss://api.openai.com/v1/realtime",
        extra_headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }

    )

    # Step: initialize the OpenAI session
    # See OpenAI’s Realtime API docs for “session.update” message format :contentReference[oaicite:1]{index=1}
    session_init = {
        "type": "session.update",
        "voice_config": {
            "voice": VOICE
        },
        "system_message": {"role": "system", "content": SYSTEM_MESSAGE},
        # Optionally: start with a greeting
    }
    await openai_ws.send(json.dumps(session_init))

    # When you want to inject availability context mid-conversation, you can send
    # "conversation.item.create" messages manually (you'll see below)

    async def forward_twilio_to_openai():
        async for msg in ws.iter_text():
            data = json.loads(msg)
            if data.get("event") == "media":
                # It's audio chunk from Twilio; forward to OpenAI
                await openai_ws.send(json.dumps({
                    "type": "input.audio",
                    "audio": data["media"]["payload"],
                    "stream_sid": data["streamSid"],
                    "timestamp": data["media"]["timestamp"]
                }))

    async def forward_openai_to_twilio():
        async for msg in openai_ws:
            data = json.loads(msg)
            # Log or debug events if you want
            # If we get "response.audio" from OpenAI, send back to Twilio
            if data.get("type") == "response.audio":
                # wrap in Twilio WebSocket protocol (send back via ws)
                await ws.send_text(json.dumps({
                    "event": "media",
                    "media": {
                        "payload": data["audio"]["payload"],
                        "timestamp": data["audio"]["timestamp"]
                    }
                }))
            # Also, we can watch for when OpenAI has generated "text" messages
            # (for us to intercept and apply booking logic)
            if data.get("type") == "response.content":
                reply_text = data["text"]["content"]
                # Check if AI’s last utterance indicates “booking”
                intent = parse_booking_intent(reply_text)
                if intent:
                    success = book_if_possible(intent)
                    if success:
                        # If booking succeeded, we might want to send a confirmation
                        confirm_text = f"Your appointment is booked with {intent['dentist']} on {intent['date']} at {intent['time']}. Thank you!"
                        # Inject text as a message in the convo
                        await openai_ws.send(json.dumps({
                            "type": "conversation.item.create",
                            "role": "assistant",
                            "content": {"type": "text", "text": confirm_text}
                        }))
                    else:
                        # If booking failed, ask clarifying question
                        msg = "I’m sorry, I couldn’t book that slot -- is there another time or dentist that works?"
                        await openai_ws.send(json.dumps({
                            "type": "conversation.item.create",
                            "role": "assistant",
                            "content": {"type": "text", "text": msg}
                        }))
            # You may also handle other event types (e.g. input_audio_buffer.speech_stopped) for interruptions

            # Kick off both coroutines
            try:
                await asyncio.gather(forward_twilio_to_openai(), forward_openai_to_twilio())
            except WebSocketDisconnect:
                pass
            finally:
                await openai_ws.close()
                await ws.close()
