from flask import Blueprint

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)
contact_bp = Blueprint('contact', __name__)

# Import route handlers
from . import main, api, contact
