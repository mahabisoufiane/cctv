from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv
from babel import Locale
import os
import logging
from logging.handlers import RotatingFileHandler

from config import config

load_dotenv()

# Initialize extensions
db = SQLAlchemy()
csrf = CSRFProtect()
mail = Mail()
migrate = Migrate()


def create_app(config_name: str = 'development') -> Flask:
    """Application factory"""
    app = Flask(__name__, template_folder='templates', static_folder='templates', static_url_path='/static')

    # Load configuration
    app_config = config.get(config_name, config['default'])
    app.config.from_object(app_config)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # CORS configuration (allow frontend on different origins)
    cors_origins = os.environ.get('CORS_ORIGINS', '').split(',') if os.environ.get('CORS_ORIGINS') else ['*']
    CORS(
        app,
        resources={r"/api/*": {"origins": cors_origins}, r"/quote": {"origins": cors_origins}},
        supports_credentials=True,
    )

    # Register blueprints
    from app.routes import main_bp, api_bp, contact_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(contact_bp)

    # Localization helper
    @app.context_processor
    def inject_globals():
        """Inject common template globals"""
        supported_languages = app_config.SUPPORTED_LANGUAGES
        return {
            'SUPPORTED_LANGUAGES': supported_languages,
            'COMPANY_NAME': app_config.COMPANY_NAME,
            'COMPANY_PHONE': app_config.COMPANY_PHONE,
            'COMPANY_EMAIL': app_config.COMPANY_EMAIL,
            'COMPANY_ADDRESS': app_config.COMPANY_ADDRESS,
            'COMPANY_CURRENCY': app_config.COMPANY_CURRENCY,
        }

    @app.before_request
    def detect_language():
        """Detect language from query param, header or default"""
        lang = request.args.get('lang') or request.accept_languages.best_match(
            list(app_config.SUPPORTED_LANGUAGES.keys())
        ) or app_config.BABEL_DEFAULT_LOCALE
        # Store in g if needed later
        from flask import g
        g.current_lang = lang

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return {'error': 'Server error'}, 500

    # Logging
    if not app.debug and not app.testing:
        log_dir = os.path.dirname(app_config.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        file_handler = RotatingFileHandler(
            app_config.LOG_FILE,
            maxBytes=app_config.LOG_MAX_SIZE,
            backupCount=10,
            encoding='utf-8',
        )
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            )
        )
        file_handler.setLevel(getattr(logging, app_config.LOG_LEVEL.upper(), logging.INFO))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, app_config.LOG_LEVEL.upper(), logging.INFO))

    return app
