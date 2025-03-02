from fastapi import APIRouter
from app.utils.training_data_loader import get_cached_training_data

# FastAPI router for training data
train_data_router = APIRouter()

# Route to upload training data
@train_data_router.get("/train-data/upload")
def train_data():
    training_data = get_cached_training_data()
    return {"message": "Training data updated successfully!"}

@train_data_router.get("/download")
def train_data():
    training_data = get_cached_training_data()
    return {"message": "Training data downloaded successfully!"}