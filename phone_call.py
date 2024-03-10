from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
import os
import openai

app = Flask(__name__)

openai.api_key = os.environ.get('OPENAI_API_KEY')

def get_ai_response(user_input):
    
    training_data = [
        {"role": "system", "content": "Hello! How can I assist you today?"},
        {"role": "user", "content": "I'm calling to cancel my credit card."},
        {"role": "system", "content": "Sure. I can help you with this. Can you please provide me with your fullname?"},
        {"role": "user", "content": "John Doe"},
        {"role": "system", "content": "Thank you, John. Can I ask why you want to cancel your credit card?"},
        {"role": "user", "content": "I think I have too many credit cards and I want to simplify my finances."},
        {"role": "system", "content": "I understand. I can help you with that. Can you please provide me with your credit card number?"},
        {"role": "user", "content": "Sure. It's 1234 5678 9101 1121"},
        {"role": "system", "content": "Thank you, John. I have successfully processed your request. Your credit card will be cancelled within 24 hours."},
        {"role": "user", "content": "Thank you."},
        {"role": "system", "content": "You're welcome. Have a great day!"}
    ]

    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=training_data + [{"role": "user", "content": user_input}],
        max_tokens=150,
        temperature=0.7,
        stop=None
    )
    return response.choices[0].message['content']

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    """Respond to incoming phone calls with a menu of options"""
    # Start our TwiML response
    resp = VoiceResponse()
    speech_result = request.values.get('SpeechResult', '').lower()

    if "thank you for helping me" in speech_result:
        resp.say("You're welcome! If you have anything else, just let me know.", voice='alice', language='en-US')
    elif "no" in speech_result:
        resp.say("Bye for now! Feel free to call us anytime.")
        resp.hangup()
    else:
        ai_response = get_ai_response(speech_result)
        resp.say(ai_response, voice='alice', language='en-US')
        
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