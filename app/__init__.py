from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
import os
from fastapi.routing import APIRouter
from contextlib import asynccontextmanager

# Import routers and register them
from app.routes.voice import voice_router
from app.routes.register import register_router
from app.routes.train_data import train_data_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize caching
    FastAPICache.init(InMemoryBackend())

    # Setup database if needed
    # db.create_all()  # Uncomment if your DB requires table creation
    
    yield  # App runs here
    
    # Cleanup actions (if necessary)

async def create_app():
    app = FastAPI(lifespan=lifespan)

    # Load config from config.py directly
    app.state.config = {
        "AZURE_STORAGE_CONTAINER":'bytheapp-training-data',
        "TRAINING_BLOB_DATA_FILE":'training_data.csv',
        "AZURE_STORAGE_VOICE_CONTAINER":'bytheapp-voice-data'
    }

    app.include_router(voice_router, prefix="/voice", tags=["voice"])
    app.include_router(register_router, prefix="/register", tags=["register"])
    app.include_router(train_data_router, prefix="/train_data", tags=["train_data"])

    return app

