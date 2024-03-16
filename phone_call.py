from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
from decorators import require_api_key
from decorators_twilio_auth import validate_twilio_request

app = Flask(__name__)

@app.route("/voice", methods=['GET', 'POST'])
#@require_api_key
@validate_twilio_request

def voice():
    """Respond to incoming phone calls with a menu of options"""
    # Start our TwiML response
    resp = VoiceResponse()

    # Directly gather speech input from the caller
    resp.say("Hello, you've reached our automated service. Please tell us how we can help you today.", voice='alice', language='en-US')
    resp.gather(input='speech', action='/respond', timeout=5, speech_timeout='auto')

    # Redirect to voice in case the gather does not execute, for example, if the caller does not say anything.
    resp.redirect('/voice')

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