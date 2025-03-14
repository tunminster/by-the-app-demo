from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from twilio.twiml.voice_response import VoiceResponse
from app.utils.decorators_twilio_auth import validate_twilio_request
import os
import openai

app = FastAPI()

openai.api_key = os.environ.get('OPENAI_API_KEY')

def get_ai_response(user_input):
    try:
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
        return str(e)  # Return the error message

@app.post("/voice")
@validate_twilio_request
async def voice(request: Request):
    """Respond to incoming phone calls with a menu of options"""
    form_data = await request.form()  # Getting form data from the request
    speech_result = form_data.get('SpeechResult', '').lower()

    resp = VoiceResponse()

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

    return HTMLResponse(str(resp))

@app.post("/respond")
async def respond(request: Request):
    """Handle speech input from the user and respond."""
    form_data = await request.form()  # Getting form data from the request
    resp = VoiceResponse()

    # Check if we have speech input
    if 'SpeechResult' in form_data:
        speech_text = form_data['SpeechResult']

        # Generate a response based on the user's speech.
        response_message = "You said: " + speech_text + ". We will process your request."

        resp.say(response_message, voice='alice', language='en-US')
    else:
        # In case there's no input, ask them to try again.
        resp.say("We didn't catch that. Could you please repeat?", voice='alice', language='en-US')
        resp.redirect('/voice')

    return HTMLResponse(str(resp))
