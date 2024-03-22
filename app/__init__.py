from flask import Flask
from .extensions import cache

def create_app():
    app = Flask(__name__)

    # Assuming config.py is at the root of your Flask app directory
    app.config.from_pyfile('config.py')
    
    # Configure and initialize caching
    app.config['CACHE_TYPE'] = 'SimpleCache' # Simple in-memory cache
    cache.init_app(app)


    from app.routes.voice import voice_bp
    app.register_blueprint(voice_bp, url_prefix='')

    from app.routes.register import register_bp
    app.register_blueprint(register_bp, url_prefix='')


    
    return app