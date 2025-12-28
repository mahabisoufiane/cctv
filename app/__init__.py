from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import timedelta

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Secret configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cctv.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Session configuration for private access
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
    
    # Private access token (change this to your secret)
    app.config['ACCESS_TOKEN'] = os.environ.get('ACCESS_TOKEN', 'cctv-demo-2025-secret')
    
    db.init_app(app)
    
    with app.app_context():
        from . import routes
        db.create_all()
    
    return app