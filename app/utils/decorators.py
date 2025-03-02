from functools import wraps
from fastapi import Request, HTTPException
import os

VALID_API_KEYS = {os.environ.get('API_SECRET_KEY')}

def require_api_key(view_function):

    @wraps(view_function)
    async def decorated_function(request: Request, *args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if api_key in VALID_API_KEYS:
            return await view_function(request, *args, **kwargs)
        else:
            raise HTTPException(status_code=401, detail="Unauthorized")
    
    return decorated_function
