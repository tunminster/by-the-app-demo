from flask import Blueprint

register_bp = Blueprint('register_bp', __name__)

@register_bp.route("/register", methods=['GET', 'POST'])
def register():
    """Register a user."""
    print("Register endpoint called")
    return "User registered successfully!"