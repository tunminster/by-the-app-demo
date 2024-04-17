from flask import Flask, request, Blueprint
from twilio.twiml.voice_response import VoiceResponse
from app.utils.decorators import require_api_key
from app.utils.decorators_twilio_auth import validate_twilio_request
from app.utils.training_data_loader import get_cached_training_data
import os
import openai
from app.utils.speech_services import synthesize_speech

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

@voice_bp.route("/voice", methods=['POST'])
#@require_api_key
@validate_twilio_request

def voice():
    """Respond to incoming phone calls with a menu of options"""
    # Start our TwiML response
    resp = VoiceResponse()
    speech_result = request.values.get('SpeechResult', '').lower()

    if "thank you for helping me" in speech_result:
        #resp.say("You're welcome! If you have anything else, just let me know.", voice='alice', language='en-US')
        audio_url = synthesize_speech("You're welcome! If you have anything else, just let me know.")
        resp.play(audio_url)
    elif "no" in speech_result:
        #resp.say("Bye for now! Feel free to call us anytime.")
        audio_url = synthesize_speech("Bye for now! Feel free to call us anytime.")
        resp.play(audio_url)
        resp.hangup()
    else:
        ai_response = get_ai_response(speech_result)
        #resp.say(ai_response, voice='alice', language='en-US')
        audio_url = synthesize_speech(ai_response)
        resp.play(audio_url)
        
        # Gather more speech input from the caller
        resp.gather(input='speech', action='/voice', timeout=10, speech_timeout='auto')
    

    # Directly gather speech input from the caller
    #resp.say("Hello, you've reached our automated service. Please tell us how we can help you today.", voice='alice', language='en-US')
    #resp.gather(input='speech', action='/respond', timeout=5, speech_timeout='auto')

    # Redirect to voice in case the gather does not execute, for example, if the caller does not say anything.
    #resp.redirect('/voice')

    return str(resp)

@app.route("/respond", methods=['GET', 'POST'])
def respond():
    """Handle speech input from the user and respond."""
    resp = VoiceResponse()

    # Check if we have speech input
    if 'SpeechResult' in request.values:
        speech_text = request.values['SpeechResult']

        # Generate a response based on the user's speech. Implement this function based on your requirements.
        response_message = "You said: " + speech_text + ". We will process your request."

        resp.say(response_message, voice='alice', language='en-US')
    else:
        # In case there's no input, ask them to try again.
        resp.say("We didn't catch that. Could you please repeat?", voice='alice', language='en-US')
        resp.redirect('/voice')

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)