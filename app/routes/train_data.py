from app.utils.training_data_loader import get_cached_training_data

train_data_bp = Blueprint('train_data_bp', __name__)

@train_data_bp.route("/train-data/upload", methods=['GET'])
def train_data():
    training_data = get_cached_training_data()

    
    return "Training data updated successfully!"