from functools import wraps
from flask import request, abort
from twilio.request_validator import RequestValidator
import os
import logging


TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_KEY')

def validate_twilio_request(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        validator = RequestValidator(TWILIO_AUTH_TOKEN)

        url = request.url

        post_vars = request.form
        signature = request.headers.get('X-Twilio-Signature', '')
        logging.debug("Twilio Signature: %s", request.headers.get('X-Twilio-Signature', ''))

        if not validator.validate(url, post_vars, signature):
            return abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function
