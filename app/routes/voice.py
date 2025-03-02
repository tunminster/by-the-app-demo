from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse, Gather
from app.utils.decorators_twilio_auth import validate_twilio_request
from app.utils.training_data_loader import get_cached_training_data
import openai
import os
from app.utils.speech_services import synthesize_speech
from app.utils.db_gather_info_helpers import VoiceHelper
from pathlib import Path
from fastapi.routing import APIRouter

# Initialize FastAPI app
voice_router = APIRouter()
# Set OpenAI API key
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Helper function to get AI response
def get_ai_response(user_input):
    try:
        training_data = get_cached_training_data()

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
@voice_router.post("/voice")
@validate_twilio_request
async def voice(request: Request):
    """Respond to incoming phone calls with a menu of options"""
    # Start our TwiML response
    resp = VoiceResponse()

    # Get caller number
    caller_number = request.query_params.get('From', 'Unknown')
    greeting = "Welcome to Our Insurance support, how can we assist you today?"
    gather = Gather(action='/handle-response', input='speech', speechTimeout="auto", method='POST')
    gather.say(greeting, voice="Polly.Joanna", language="en-US")
    resp.append(gather)

    # If user does not respond, repeat question and redirect
    resp.say("I'm sorry, I didn't hear anything. Let me try again.", voice="Polly.Joanna", language="en-US")
    resp.redirect("/voice")

    return PlainTextResponse(str(resp))

# Handle user response after gathering input
@voice_router.post("/handle-response")
async def handle_response(request: Request):
    user_speech = request.query_params.get("SpeechResult", "")
    bot_reply = get_ai_response(user_speech)

    """Handle speech input from the user and response."""
    resp = VoiceResponse()
    resp.say(bot_reply, voice="Polly.Joanna", language="en-US")

    gather = Gather(input="speech", action="/handle-response", speechTimeout="auto")
    gather.say("Would you like any further assistance?", voice="Polly.Joanna", language="en-US")
    resp.append(gather)

    return PlainTextResponse(str(resp))

# Route when no response is detected
@voice_router.post("/no-response")
async def no_response():
    resp = VoiceResponse()

    # First attempt to re-engage
    gather = resp.gather(action='/handle-response', method='POST', input='speech', timeout=20)
    gather.say("Hello, are you still there? Please let us know how we can assist you.", voice='alice', language='en-US')

    # If still no response, redirect to a final warning route
    resp.redirect('/final-warning')

    return PlainTextResponse(str(resp))

# Final warning route when there’s still no response
@voice_router.post("/final-warning")
async def final_warning():
    resp = VoiceResponse()

    # Final attempt to re-engage
    gather = resp.gather(action='/handle-response', method='POST', input='speech', timeout=20)
    gather.say("We have not heard from you. Please speak to continue. We will disconnect the call in 2 minutes if there is no response.", voice='alice', language='en-US')

    # Set up the hang-up if no response after final warning
    resp.redirect('/hang-up')

    return PlainTextResponse(str(resp))

# Hang-up route
@voice_router.post("/hang-up")
async def hang_up():
    resp = VoiceResponse()
    resp.say("No response detected, we are now disconnecting the call. Goodbye!", voice='alice', language='en-US')
    resp.hangup()

    return PlainTextResponse(str(resp))

# Function to generate speech and save to a file
def generate_speech(text, filename):
    """Generate speech using OpenAI and save to a static file."""
    speech_file_path = Path(__file__).resolve().parent.parent / "static" / filename
    response = openai.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    response.stream_to_file(speech_file_path)
    return filename

# Helper function to check if the call should end
def should_end_call(ai_response):
    lower_response = ai_response.lower()
    if "goodbye" in lower_response or "goodbye!" in lower_response:
        return True
    return False
