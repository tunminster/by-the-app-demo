from functools import wraps
from flask import request, abort
from twilio.request_validator import RequestValidator
import os
import logging
logging.basicConfig(level=logging.INFO)


TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_KEY')

def validate_twilio_request(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        validator = RequestValidator(TWILIO_AUTH_TOKEN)

        forwarded_proto = request.headers.get('X-Forwarded-Proto', '')
        if forwarded_proto == 'https':
            url = request.url.replace("http://", "https://")
        else:
            url = request.url

        post_vars = request.form.to_dict()
        signature = request.headers.get('X-Twilio-Signature', '')
        logging.info("Twilio Signature: %s", request.headers.get('X-Twilio-Signature', ''))
        logging.info("Twilio URL: %s", request.url)
        logging.info("Twilio POST Vars: %s", request.form.to_dict())

        if not validator.validate(url, post_vars, signature):
            return abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function
