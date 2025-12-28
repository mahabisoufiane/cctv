from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import os
from datetime import timedelta

db = SQLAlchemy()
mail = Mail()

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
    
    # Flask-Mail Configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', True)
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@cctvsystem.ma')
    
    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    
    with app.app_context():
        # Import and register blueprints
        from .routes import main_bp, api_bp, contact_bp, admin_bp, technician_bp, payment_bp
        app.register_blueprint(main_bp)
        app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(contact_bp)
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(technician_bp, url_prefix='/technician')
        app.register_blueprint(payment_bp, url_prefix='/payment')
        
        db.create_all()
    
    return app
