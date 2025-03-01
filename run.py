from app import app  # Import your FastAPI app from the main app module
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80, reload=True)
