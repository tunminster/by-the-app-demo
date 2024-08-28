from flask import Flask, request, Blueprint, url_for
from twilio.twiml.voice_response import VoiceResponse,Gather
from app.utils.decorators import require_api_key
from app.utils.decorators_twilio_auth import validate_twilio_request
from app.utils.training_data_loader import get_cached_training_data
import os
import openai
from app.utils.speech_services import synthesize_speech
from app.utils.db_gather_info_helpers import VoiceHelper
from app.utils.db_setup import db
from pathlib import Path

app = Flask(__name__)

openai.api_key = os.environ.get('OPENAI_API_KEY')

def get_ai_response(user_input):
    
    
    try:
        training_data = get_cached_training_data()

        # Prepare the conversation history as a prompt
        conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in training_data])
        conversation_history += f"\nuser: {user_input}\nsystem:"

        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=training_data + [{"role": "user", "content": user_input}],
            max_tokens=150,
            temperature=0.7,
            stop=None
        )

        return response.choices[0].message.content
    except Exception as e:
        print(e)
        return e.message

voice_bp = Blueprint('voice_bp', __name__)

@voice_bp.route("/voice", methods=['GET','POST'])
#@require_api_key
@validate_twilio_request
def voice():
    """Respond to incoming phone calls with a menu of options"""
    # Start our TwiML response
    resp = VoiceResponse()

    gather = resp.gather(action='/handle-response', input='speech', timeout=10, method='POST')

    greeting = "Welcome to ABC Bank, how can we assist you today?"
    path_to_speech = generate_speech(greeting, "welcome.mp3")

    gather.play(url_for('static', filename=path_to_speech, _external=True))
    resp.append(gather)

    return str(resp)

@voice_bp.route("/handle-response", methods=['GET', 'POST'])
def handle_response():
    """Handle speech input from the user and response."""
    resp = VoiceResponse()
    
    speech_result = request.values.get('SpeechResult', '').lower()
    
    if "thank you for helping me" in speech_result:
        thanks_response = "You're welcome! If you have anything else, just let me know."
        path_to_speech = generate_speech(thanks_response, "thanks.mp3")
        resp.play(url_for('static', filename=path_to_speech, _external=True))
    else:
        # Generate response based on AI and customer's input
        ai_response = get_ai_response(speech_result)
        path_to_speech = generate_speech(ai_response, "response.mp3")
        resp.play(url_for('static', filename=path_to_speech, _external=True))

        # Gather more input
        gather = Gather(input='speech', action='/handle-response', timeout=10, speech_timeout='auto')
        resp.append(gather)

    return str(resp)

@voice_bp.route("/no-response", methods=['GET', 'POST'])
def no_response():
    resp = VoiceResponse()

    # First attempt to re-engage
    gather = resp.gather(action='/handle-response', method='POST', input='speech', timeout=20)

    gather.say("Hello, are you still there? Please let us know how we can assist you.", voice='alice', language='en-US')

    # If still no response, redirect to a final warning route
    resp.redirect('/final-warning')

    return str(resp)

@voice_bp.route("/final-warning", methods=['GET', 'POST'])
def final_warning():
    resp = VoiceResponse()

    # Final attempt to re-engage
    gather = resp.gather(action='/handle-response', method='POST', input='speech', timeout=20)

    gather.say("We have not heard from you. Please speak to continue. We will disconnect the call in 2 minutes if there is no response.", voice='alice', language='en-US')

    # Set up the hang-up if no response after final warning
    resp.redirect('/hang-up')

    return str(resp)

@voice_bp.route("/hang-up", methods=['GET', 'POST'])
def hand_up():
    resp = VoiceResponse()
    resp.say("No response detected, we are now disconnecting the call. Goodbye!", voice='alice', language='en-US')
    resp.hangup()

    return str(resp)

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


def should_end_call(ai_response):
    # Lowercase to standardize the input for comparison
    lower_response = ai_response.lower()
    # Check for phrases that indicate ending the call
    if "goodbye" in lower_response or "goodbye!" in lower_response:
        return True
    return False


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)