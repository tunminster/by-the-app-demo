from fastapi import FastAPI
from fastapi_cache2 import FastAPICache
from fastapi_cache2.backends.inmemory import InMemoryBackend
from .utils.db_setup import db, CallInfo
import os
from fastapi.routing import APIRouter

app = FastAPI()

    # Load config from config.py directly
app.state.config = {
    "AZURE_STORAGE_CONTAINER":'bytheapp-training-data',
    "TRAINING_BLOB_DATA_FILE":'training_data.csv',
    "AZURE_STORAGE_VOICE_CONTAINER":'bytheapp-voice-data'
}

# Initialize caching (alternative to Flask-Caching)
@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend())

# Database and table setup (if required)
@app.on_event("startup")
async def startup():
    # Create tables if necessary
    # db.create_all()  # Uncomment if needed with your DB setup
    pass

# Import routers and register them
from app.routes.voice import voice_router
from app.routes.register import register_router
from app.routes.train_data import train_data_router

app.include_router(voice_router, prefix="/voice", tags=["voice"])
app.include_router(register_router, prefix="/register", tags=["register"])
app.include_router(train_data_router, prefix="/train_data", tags=["train_data"])