from flask import Flask
from fastapi import FastAPI
from .extensions import cache
from .utils.db_setup import db, CallInfo
import os
from fastapi.routing import APIRouter

def create_app():
    #app = Flask(__name__)

    app = FastAPI()

    # Assuming config.py is at the root of your Flask app directory
    app.config.from_pyfile('config.py')

    # Configure and initialize caching
    app.config['CACHE_TYPE'] = 'SimpleCache'

    cache.init_app(app)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"{os.environ.get('SQLALCHEMY_DATABASE_URI')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    #if os.getenv('FLASK_ENV') == 'development':
        #with app.app_context():
            #db.create_all()  # Create tables if not already present



    from app.routes.voice import voice_bp
    app.register_blueprint(voice_bp, url_prefix='')

    from app.routes.register import register_bp
    app.register_blueprint(register_bp, url_prefix='')

    from app.routes.train_data import train_data_bp
    app.register_blueprint(train_data_bp, url_prefix='')


    
    return app