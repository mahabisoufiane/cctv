from flask import Flask, g, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_cors import CORS
from config import config
import logging
from datetime import datetime

db = SQLAlchemy()
mail = Mail()

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    CORS(app)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Register blueprints
    from app.routes import main_bp, api_bp, contact_bp, admin_bp, technician_bp, payment_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(contact_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(technician_bp, url_prefix='/technician')
    app.register_blueprint(payment_bp, url_prefix='/payment')
    
    # Middleware for language detection
    @app.before_request
    def before_request():
        # Get language from query parameter or default to 'ar'
        lang = request.args.get('lang', 'ar')
        if lang not in ['ar', 'fr', 'en']:
            lang = 'ar'
        g.current_lang = lang
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {'success': False, 'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'success': False, 'error': 'Internal server error'}, 500
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
