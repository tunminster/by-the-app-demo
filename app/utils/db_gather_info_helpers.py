from twilio.twiml.voice_response import VoiceResponse

class VoiceHelper:
    @staticmethod
    def gather_info(session, speech_result):
        resp = VoiceResponse()
        prompt = ""

        if 'full name' in session.get('last_ai_prompt', ''):
            session['full_name'] = speech_result
            session['last_ai_prompt'] = 'date of birth'
            prompt = "Thank you. Now please tell me your date of birth in the format of month, day, and year."
        elif 'date of birth' in session.get('last_ai_prompt', ''):
            session['date_of_birth'] = speech_result
            session['last_ai_prompt'] = 'last four digits'
            prompt = "Got it. Now please provide the last four digits of your credit card."
        elif 'last four digits' in session.get('last_ai_prompt', ''):
            session['last_four_cc_digits'] = speech_result
            session['last_ai_prompt'] = 'contact number'
            prompt = "Thank you. Finally, please provide your contact number."
        elif 'contact number' in session.get('last_ai_prompt', ''):
            session['contact_number'] = speech_result
            session['last_ai_prompt'] = None

            VoiceHelper.save_call_info(session, db)
            prompt = "Thank you for providing all the required information. We will process your request and get back to you shortly. Also, you will be confirmation email soon. Do you need any other assistance while we are in the call?"
        
        resp.say(prompt, voice='alice', language='en-US')
        resp.gather(input='speech', action='/handle-response', timeout=20, method='POST')
        return str(resp)
    
    @staticmethod
    def save_call_info(session,db):
        from .utils.db_setup import CallInfo
        call_info = CallInfo(
            full_name=session['full_name'],
            date_of_birth=session['date_of_birth'],
            last_four_cc_digits=session['last_four_cc_digits'],
            contact_number=session['contact_number'],
            action_to_do=session['action_to_do']
        )
        db.session.add(call_info)
        db.session.commit()
        return "User registered successfully!"

