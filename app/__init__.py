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
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize caching
    FastAPICache.init(InMemoryBackend())

    # Setup database if needed
    # db.create_all()  # Uncomment if your DB requires table creation
    
    yield  # App runs here
    
    # Cleanup actions (if necessary)

def create_app():
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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow only your frontend domain
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
    )

    print("📌 Registered Routes:")
    for route in app.routes:
        if hasattr(route, "methods"):
            print(f"{route.path} -> {route.name} ({route.methods})")
        else:
            print(f"{route.path} -> {route.name} (WebSocket or custom route)")

    return app

