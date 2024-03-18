from functools import wraps
from flask import request, abort
import os

VALID_API_KEYS = { os.environ.get('API_SECRET_KEY')}

def require_api_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request. headers.get('X-API-KEY') in VALID_API_KEYS:
            return view_function(*args, **kwargs)
        else:
            abort(401)
    return decorated_function
