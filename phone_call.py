from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    """Respond to incoming phone calls with a menu of options"""
    # Start our TwiML response
    resp = VoiceResponse()

    # Start our <Gather> verb
    with resp.gather(numDigits=1, action='/gather') as gather:
        gather.say('For sales, press 1. For support, press 2.')

    # If the user doesn't select an option, redirect them into a loop
    resp.redirect('/voice')

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)