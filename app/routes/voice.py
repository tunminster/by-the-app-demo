import os
import json
import asyncio
import websockets
import base64
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
#@validate_twilio_request
async def voice(request: Request):
    """
    Twilio will call this webhook when a call arrives.
    We'll return TwiML to instruct Twilio to stream media to our /media-stream WS endpoint.
    """
    host = request.url.hostname
    vr = VoiceResponse()

    vr.say("Welcome to the dental office. Please wait while we connect you to our AI assistant.", voice=VOICE)
    connect = Connect()

    connect.stream(url=f"wss://{host}/voice/media-stream")
    vr.append(connect)

    return HTMLResponse(content=str(vr), media_type="application/xml")

@voice_router.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    """
    WebSocket endpoint Twilio will send media to.
    We’ll also connect to OpenAI Realtime and proxy audio both ways.
    We’ll insert booking logic by interjecting system/context messages if needed.
    """
    await websocket.accept()
    print("🎧 Client connected to /media-stream")

    openai_ws_url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview"
    headers = [("Authorization", f"Bearer {OPENAI_API_KEY}")]

    try:
        async with websockets.connect(openai_ws_url, additional_headers=headers) as openai_ws:
            print("🔗 Connected to OpenAI Realtime API")

            # 1️⃣ Initialize session
            session_init = {
                "type": "session.update",
                "model": "gpt-4o-realtime-preview",
                "voice": VOICE,
                "instructions": SYSTEM_MESSAGE,
                "metadata": {}
            }
            await openai_ws.send(json.dumps(session_init))
            print("📤 Sent session.init to OpenAI")

            session_id = None

            async def handle_openai_responses():
                while True:
                    msg = await openai_ws.recv()
                    event = json.loads(msg)

                    # Capture session ID
                    if event.get("type") == "session.created":
                        nonlocal session_id
                        session_id = event["session"]["id"]
                        print("✅ OpenAI session created:", session_id)

                    # If OpenAI returns audio data, send to Twilio
                    if event.get("type") == "response.audio.buffer":
                        audio_bytes = base64.b64decode(event["audio"]["data"])
                        twilio_event = {
                            "event": "media",
                            "media": {
                                "payload": base64.b64encode(audio_bytes).decode("utf-8"),
                                "track": "outbound_track"
                            }
                        }
                        await websocket.send_text(json.dumps(twilio_event))

            

            async def handle_twilio_messages():
                while True:
                    data = await websocket.receive_text()
                    twilio_event = json.loads(data)

                    # Only handle media events from Twilio
                    if twilio_event.get("event") == "media":
                        audio_b64 = twilio_event["media"]["payload"]
                        audio_bytes = base64.b64decode(audio_b64)

                        # Forward to OpenAI Realtime as audio
                        if session_id:
                            event_to_openai = {
                                "type": "input_audio_buffer.append",
                                "audio": {
                                    "content": base64.b64encode(audio_bytes).decode("utf-8")
                                }
                            }
                            await openai_ws.send(json.dumps(event_to_openai))

                    # Handle end of segment / process
                    elif twilio_event.get("event") == "stop":
                        if session_id:
                            await openai_ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
                            await openai_ws.send(json.dumps({"type": "response.create"}))
            await asyncio.gather(
                handle_openai_responses(),
                handle_twilio_messages()
            )

    except websockets.ConnectionClosedError as e:
        print("❌ OpenAI WebSocket closed:", e)
    finally:
        await websocket.close()
        print("🛑 Client disconnected")
