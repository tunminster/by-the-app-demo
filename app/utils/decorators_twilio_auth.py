from functools import wraps
from fastapi import Request, HTTPException
from twilio.request_validator import RequestValidator
import os
import logging

logging.basicConfig(level=logging.INFO)

TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_KEY')

def validate_twilio_request(f):

    @wraps(f)
    async def decorated_function(request: Request, *args, **kwargs):
        validator = RequestValidator(TWILIO_AUTH_TOKEN)

        forwarded_proto = request.headers.get('X-Forwarded-Proto', '')
        if forwarded_proto == 'https':
            url = str(request.url).replace("http://", "https://")
        else:
            url = str(request.url)

        post_vars = await request.form()
        signature = request.headers.get('X-Twilio-Signature', '')
        logging.info("Twilio Signature: %s", signature)
        logging.info("Twilio URL: %s", url)
        logging.info("Twilio POST Vars: %s", post_vars)

        if not validator.validate(url, post_vars, signature):
            raise HTTPException(status_code=403, detail="Forbidden")

        return await f(request, *args, **kwargs)
    
    return decorated_function
