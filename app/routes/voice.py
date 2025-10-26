import os
import json
import asyncio
import websockets
import base64
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse, HTMLResponse
from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream, Gather
from app.utils.decorators_twilio_auth import validate_twilio_request
from app.utils.training_data_loader import get_cached_training_data
import openai
import audioop
import re


from app.utils.speech_services import synthesize_speech
from pathlib import Path
from fastapi.routing import APIRouter
from app.utils.db import fetch_available_slots, fetch_dentists, find_patient_by_name, find_patient_by_phone, find_patient_by_email, create_new_patient
from app.utils.booking import build_context_text, parse_booking_intent, parse_booking_intent_ai, book_if_possible
from app.utils.kafka_producer import ai_response_producer

# Initialize FastAPI app
voice_router = APIRouter()
# Set OpenAI API key
openai.api_key = os.environ.get('OPENAI_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
SYSTEM_MESSAGE = """
    You are a helpful dental receptionist. Use the availability to schedule appointments for patients. Ask clarifying questions if needed. 
    When the patient agrees to book, ALWAYS send a hidden message in the format: 
    BOOKING_CONFIRMATION: {"dentist": "Dr. Sarah Nguyen", "date": "2025-10-25", "time": "10:00", "patient_name": "Alice Jones"} 
    Do not say this out loud. Just include it as a text output message.
    """
VOICE = "alloy"
PORT = int(os.getenv("PORT", 5050))
TEMPERATURE = float(os.getenv('TEMPERATURE', 0.8))
LOG_EVENT_TYPES = [
    'error', 'response.content.done', 'rate_limits.updated',
    'response.done', 'input_audio_buffer.committed',
    'input_audio_buffer.speech_stopped', 'input_audio_buffer.speech_started',
    'session.created', 'session.updated'
]
SHOW_TIMING_MATH = False


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

    vr.say("Welcome to the dental office. Please wait while we connect you to our AI assistant.", voice="Google.en-US-Chirp3-HD-Aoede")
    vr.pause(length=1)
    vr.say(   
        "O.K. you can start talking!",
        voice="Google.en-US-Chirp3-HD-Aoede"
    )
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
    print("🎧 Twilio client connected")

    openai_ws_url = "wss://api.openai.com/v1/realtime?model=gpt-realtime&temperature={TEMPERATURE}"
    headers = [("Authorization", f"Bearer {OPENAI_API_KEY}")]
    session_id = None
    pending_audio = []

    try:
        async with websockets.connect(openai_ws_url, additional_headers=headers) as openai_ws:
            print("🔗 Connected to OpenAI Realtime API")

            await initialize_session(openai_ws)

            # Connection specific state
            stream_sid = None
            latest_media_timestamp = 0
            last_assistant_item = None
            mark_queue = []
            response_start_timestamp_twilio = None

            # Handle OpenAI responses
            async def receive_from_twilio():
                """Receive audio data from Twilio and send it to the OpenAI Realtime API."""
                nonlocal stream_sid, latest_media_timestamp
                try:
                    async for message in websocket.iter_text():
                        data = json.loads(message)
                        if data['event'] == 'media' and openai_ws.state.name == 'OPEN':
                            latest_media_timestamp = int(data['media']['timestamp'])
                            audio_append = {
                                "type": "input_audio_buffer.append",
                                "audio": data['media']['payload']
                            }
                            await openai_ws.send(json.dumps(audio_append))
                        elif data['event'] == 'start':
                            stream_sid = data['start']['streamSid']
                            print(f"Incoming stream has started {stream_sid}")
                            response_start_timestamp_twilio = None
                            latest_media_timestamp = 0
                            last_assistant_item = None
                        elif data['event'] == 'mark':
                            if mark_queue:
                                mark_queue.pop(0)
                except WebSocketDisconnect:
                    print("Client disconnected.")
                    if openai_ws.state.name == 'OPEN':
                        await openai_ws.close()

            async def send_to_twilio():
                """Receive events from the OpenAI Realtime API, send audio back to Twilio."""
                nonlocal stream_sid, last_assistant_item, response_start_timestamp_twilio
                try:
                    async for openai_message in openai_ws:
                        response = json.loads(openai_message)
                        if response['type'] in LOG_EVENT_TYPES:
                            print(f"Received event: {response['type']}", response)

                        # 🔹 Handle RAG text responses
                        await process_ai_text_response(openai_ws, response)

                        if response.get('type') == 'response.output_audio.delta' and 'delta' in response:
                            audio_payload = base64.b64encode(base64.b64decode(response['delta'])).decode('utf-8')
                            audio_delta = {
                                "event": "media",
                                "streamSid": stream_sid,
                                "media": {
                                    "payload": audio_payload
                                }
                            }
                            await websocket.send_json(audio_delta)


                            if response.get("item_id") and response["item_id"] != last_assistant_item:
                                response_start_timestamp_twilio = latest_media_timestamp
                                last_assistant_item = response["item_id"]
                                if SHOW_TIMING_MATH:
                                    print(f"Setting start timestamp for new response: {response_start_timestamp_twilio}ms")

                            await send_mark(websocket, stream_sid)

                        # Trigger an interruption. Your use case might work better using `input_audio_buffer.speech_stopped`, or combining the two.
                        if response.get('type') == 'input_audio_buffer.speech_started':
                            print("Speech started detected.")
                            if last_assistant_item:
                                print(f"Interrupting response with id: {last_assistant_item}")
                                await handle_speech_started_event()
                except Exception as e:
                    print(f"Error in send_to_twilio: {e}")

            async def handle_speech_started_event():
                """Handle interruption when the caller's speech starts."""
                nonlocal response_start_timestamp_twilio, last_assistant_item
                print("Handling speech started event.")
                if mark_queue and response_start_timestamp_twilio is not None:
                    elapsed_time = latest_media_timestamp - response_start_timestamp_twilio
                    if SHOW_TIMING_MATH:
                        print(f"Calculating elapsed time for truncation: {latest_media_timestamp} - {response_start_timestamp_twilio} = {elapsed_time}ms")

                    if last_assistant_item:
                        if SHOW_TIMING_MATH:
                            print(f"Truncating item with ID: {last_assistant_item}, Truncated at: {elapsed_time}ms")

                        truncate_event = {
                            "type": "conversation.item.truncate",
                            "item_id": last_assistant_item,
                            "content_index": 0,
                            "audio_end_ms": elapsed_time
                        }
                        await openai_ws.send(json.dumps(truncate_event))

                    await websocket.send_json({
                        "event": "clear",
                        "streamSid": stream_sid
                    })

                    mark_queue.clear()
                    last_assistant_item = None
                    response_start_timestamp_twilio = None
            
            async def send_mark(connection, stream_sid):
                if stream_sid:
                    mark_event = {
                        "event": "mark",
                        "streamSid": stream_sid,
                        "mark": {"name": "responsePart"}
                    }
                    await connection.send_json(mark_event)
                    mark_queue.append('responsePart')
            # Run both loops concurrently
            await asyncio.gather(receive_from_twilio(), send_to_twilio())

    except websockets.ConnectionClosedError as e:
        print("❌ OpenAI WebSocket closed:", e)
    finally:
        await websocket.close()
        print("🛑 Twilio client disconnected")


async def initialize_session(openai_ws):
    """Control initial session with OpenAI."""
    session_update = {
        "type": "session.update",
        "session": {
            "type": "realtime",
            "model": "gpt-realtime",
            "output_modalities": ["audio"],
            "audio": {
                "input": {
                    "format": {"type": "audio/pcmu"},
                    "turn_detection": {"type": "server_vad"}
                },
                "output": {
                    "format": {"type": "audio/pcmu"},
                    "voice": VOICE
                }
            },
            "instructions": SYSTEM_MESSAGE,
        }
    }
    print('Sending session update:', json.dumps(session_update))
    await openai_ws.send(json.dumps(session_update))

    # Inject dynamic RAG context (availability from DB)
    await inject_availability_context(openai_ws)
    
    # Inject patient lookup context (will be called again with actual caller info when available)
    await inject_patient_context(openai_ws)

    # Uncomment the next line to have the AI speak first
    await send_initial_conversation_item(openai_ws)

async def send_initial_conversation_item(openai_ws):
    """Send initial conversation item if AI talks first."""
    initial_conversation_item = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "Greet the user with 'Hello there! I am an AI voice assistant. How can I help you?'"
                }
            ]
        }
    }
    await openai_ws.send(json.dumps(initial_conversation_item))
    await openai_ws.send(json.dumps({"type": "response.create"}))

async def process_ai_text_response(openai_ws, response, call_id=None):
    """
    Handle AI text responses: send entire response to Kafka for processing.
    """
    try:
        if response.get("type") == "response.done":

            output = response.get("response", {}).get("output", [])
            text_chunk = []
            for item in output:
                if item.get("type") == "message":
                    for c in item.get("content", []):
                        if c.get("type") == "output_audio" and "transcript" in c:
                            text_chunk.append(c["transcript"])

            print("🧾 AI said:", text_chunk)

            text_chunk = "".join(text_chunk)
            print("text_chunk ", text_chunk)

            # Send entire AI response to Kafka for processing
            success = ai_response_producer.send_ai_response(
                call_id=call_id or "unknown",
                response_type="AI_RESPONSE",
                data={
                    "raw_text": text_chunk,
                    "full_response": response,
                    "timestamp": datetime.now().isoformat()
                },
                metadata={
                    "source": "voice_ai",
                    "call_id": call_id or "unknown",
                    "response_type": "complete_ai_response"
                }
            )
            
            if success:
                print("✅ AI response sent to Kafka for processing")
                # Send confirmation to AI
                await send_processing_confirmation(openai_ws)
            else:
                print("❌ Failed to send AI response to Kafka")
                
    except Exception as e:
        print(f"❌ Error processing AI response: {e}")

async def inject_availability_context(openai_ws, limit=5):
    """
    Fetch available dentist slots from DB and inject as RAG context into OpenAI session.
    """
    try:
        # 1️⃣ Fetch slots
        slots = fetch_available_slots(limit=limit)
        if slots:
            availability_text = build_context_text(slots)
        else:
            availability_text = "Currently no available appointments."

        # 2️⃣ Fetch dentists with specialties
        dentists = fetch_dentists()
        if dentists:
            dentist_info = "\n".join([f"{d['name']} ({d['specialty']})" for d in dentists])
        else:
            dentist_info = "No dentists found."

        context_text = f"Available appointments:\n{availability_text}\n\nDentists in this office:\n{dentist_info}"

        context_message = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                         "text": (
                            f"Here are the available appointments:\n{context_text}\n\n"
                            "When booking an appointment, always ask for the patient's full name "
                            "if it has not been provided. Use this name when saving the appointment."
                        )
                    }
                ]
            }
        }

        await openai_ws.send(json.dumps(context_message))
        print("✅ Injected RAG context (availability) into conversation.")
    except Exception as e:
        print(f"❌ Failed to inject RAG context: {e}")

async def inject_patient_context(openai_ws, caller_name=None, caller_phone=None):
    """
    Inject patient lookup context to help AI determine if caller is new or existing patient.
    """
    try:
        patient_context = ""
        existing_patients = []
        
        # If we have a name, search for existing patients
        if caller_name:
            patients_by_name = find_patient_by_name(caller_name)
            existing_patients.extend(patients_by_name)
        
        # If we have a phone, search for existing patients
        if caller_phone:
            patient_by_phone = find_patient_by_phone(caller_phone)
            if patient_by_phone and patient_by_phone not in existing_patients:
                existing_patients.append(patient_by_phone)
        
        if existing_patients:
            patient_info = "\n".join([
                f"Patient: {p['name']}, Phone: {p['phone']}, Email: {p['email']}, DOB: {p['date_of_birth']}, Status: {p['status']}"
                for p in existing_patients
            ])
            patient_context = f"EXISTING PATIENTS FOUND:\n{patient_info}\n\n"
        else:
            patient_context = "NO EXISTING PATIENTS FOUND - This appears to be a new patient.\n\n"
        
        context_message = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            f"{patient_context}"
                            "PATIENT VERIFICATION INSTRUCTIONS:\n"
                            "1. If existing patients are found above, confirm their details (name, phone, email, date of birth)\n"
                            "2. If no existing patients found, collect NEW PATIENT information:\n"
                            "   - Full name\n"
                            "   - Phone number\n"
                            "   - Email address\n"
                            "   - Date of birth (MM/DD/YYYY format)\n"
                            "3. For new patients, say: 'I'll need to create a new patient record for you. Let me collect your information.'\n"
                            "4. For existing patients, say: 'I found your record. Let me confirm your details.'\n"
                            "5. Always verify the information before proceeding with appointment booking.\n"
                            "6. If creating a new patient, use the collected information to create the patient record before booking.\n"
                            "7. When you have collected all patient information, output exactly this format (do not speak this out loud):\n"
                            "PATIENT_CREATION: {\"name\": \"John Smith\", \"email\": \"john@email.com\", \"phone\": \"(555) 123-4567\", \"date_of_birth\": \"01/15/1985\"}"
                        )
                    }
                ]
            }
        }
        
        await openai_ws.send(json.dumps(context_message))
        print("✅ Injected RAG context (patient lookup) into conversation.")
    except Exception as e:
        print(f"❌ Error injecting patient context: {e}")

async def create_patient_from_ai_response(openai_ws, patient_data):
    """
    Create a new patient record from AI-collected data.
    """
    try:
        # Extract patient information from AI response
        name = patient_data.get('name', '').strip()
        email = patient_data.get('email', '').strip()
        phone = patient_data.get('phone', '').strip()
        date_of_birth = patient_data.get('date_of_birth', '').strip()
        
        if not all([name, email, phone, date_of_birth]):
            raise ValueError("Missing required patient information")
        
        # Create the patient record
        patient_id = create_new_patient(name, email, phone, date_of_birth)
        
        if patient_id:
            # Send confirmation to AI
            confirmation_message = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                f"✅ NEW PATIENT CREATED SUCCESSFULLY!\n"
                                f"Patient ID: {patient_id}\n"
                                f"Name: {name}\n"
                                f"Email: {email}\n"
                                f"Phone: {phone}\n"
                                f"Date of Birth: {date_of_birth}\n\n"
                                "You can now proceed with booking the appointment for this patient."
                            )
                        }
                    ]
                }
            }
            await openai_ws.send(json.dumps(confirmation_message))
            print(f"✅ Created new patient: {name} (ID: {patient_id})")
            return patient_id
        else:
            raise Exception("Failed to create patient record")
            
    except Exception as e:
        error_message = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"❌ ERROR: Failed to create patient record: {str(e)}\nPlease ask the caller to provide the information again."
                    }
                ]
            }
        }
        await openai_ws.send(json.dumps(error_message))
        print(f"❌ Error creating patient: {e}")
        return None

async def send_processing_confirmation(openai_ws):
    """
    Send confirmation to AI that response was sent to Kafka for processing.
    """
    try:
        confirmation_message = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": "✅ Your response has been sent for processing. I'm analyzing your request and will handle any patient creation or appointment booking as needed."
                    }
                ]
            }
        }
        await openai_ws.send(json.dumps(confirmation_message))
        print("✅ Sent processing confirmation to AI")
    except Exception as e:
        print(f"❌ Error sending processing confirmation: {e}")