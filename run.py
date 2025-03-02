from app import create_app  # Import the function, not the app instance
from fastapi_cache2 import FastAPICache
from fastapi_cache2.backends.inmemory import InMemoryBackend

import uvicorn

app = create_app()  # Call the function to create the FastAPI app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80, reload=True)
