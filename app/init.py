from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging

load_dotenv()

# Initialize extensions
db = SQLAlchemy()
csrf = CSRFProtect()
mail = Mail()

def create_app(config_name='development'):
    """Create and configure Flask app"""
    
    # Get absolute paths for templates and static
    template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    
    # Create Flask app with explicit paths
    app = Flask(__name__, 
                template_folder=template_path,
                static_folder=static_path,
                static_url_path='/static')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///camerasecurity.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Mail configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')
    
    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}, r"/quote": {"origins": "*"}})
    
    # Register blueprints (routes)
    from app.routes.init import main_bp, api_bp, contact_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(contact_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return {'error': 'Server error'}, 500
    
    # Setup logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler('logs/camerasecurity.log', maxBytes=10240000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
    
    return app
