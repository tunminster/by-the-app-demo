import uvicorn
from app import create_app  # Import the function, not the app instance

if __name__ == "__main__":
    uvicorn.run("app:create_app", host="0.0.0.0", port=80, reload=True, factory=True)
    