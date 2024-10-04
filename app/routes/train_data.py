from flask import Flask, request, Blueprint, url_for
from app.utils.training_data_loader import get_cached_training_data

train_data_bp = Blueprint('train_data_bp', __name__)

@train_data_bp.route("/train-data", methods=['POST'])
def train_data():
    training_data = get_cached_training_data()

    
    print("Train data endpoint called")
    return "Training data updated successfully!"