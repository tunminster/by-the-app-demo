from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
import os
from fastapi.routing import APIRouter
from contextlib import asynccontextmanager

# Import routers and register them
from app.routes.voice import voice_router

from app.routes.auth import auth_router
from app.routes.dentist import dentist_router
from app.routes.user import user_router
from app.routes.patient import patient_router
from app.routes.availability import availability_router
from app.routes.appointment import appointment_router
from app.routes.dashboard import dashboard_router
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
    app.include_router(auth_router, prefix="/auth", tags=["authentication"])
    app.include_router(dentist_router, prefix="/api", tags=["dentists"])
    app.include_router(user_router, prefix="/api", tags=["users"])
    app.include_router(patient_router, prefix="/api", tags=["patients"])
    app.include_router(availability_router, prefix="/api", tags=["availability"])
    app.include_router(appointment_router, prefix="/api", tags=["appointments"])
    app.include_router(dashboard_router, prefix="/api", tags=["dashboard"])

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

