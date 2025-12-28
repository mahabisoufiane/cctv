from flask import Blueprint

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)
contact_bp = Blueprint('contact', __name__)
admin_bp = Blueprint('admin', __name__)
technician_bp = Blueprint('technician', __name__)
payment_bp = Blueprint('payment', __name__)

# Import routes to register them
from . import main, api, contact, admin, technician, payment
