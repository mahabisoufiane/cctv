from flask import request, jsonify, current_app, render_template
from app.routes.init import contact_bp
from app.models import QuoteRequest
from app.init import db, mail
from flask_mail import Message
import re

def validate_email(email):
    """Simple email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Simple phone validation"""
    pattern = r'^[\d\s\-\+\(\)]+$'
    return re.match(pattern, phone) is not None

@contact_bp.route('/quote', methods=['POST'])
def submit_quote():
    """Handle quote request submission"""
    try:
        data = request.get_json()
        
        # Get form data
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        service = data.get('service', '').strip()
        message = data.get('message', '').strip()
        location_id = data.get('location_id')
        camera_count = data.get('camera_count')
        resolution = data.get('resolution')
        difficulty = data.get('difficulty_level')
        estimated_price = data.get('estimated_price')
        
        # Validate
        errors = {}
        
        if not name or len(name) < 2 or len(name) > 100:
            errors['name'] = 'Name must be 2-100 characters'
        
        if not email or not validate_email(email):
            errors['email'] = 'Valid email required'
        
        if not phone or not validate_phone(phone):
            errors['phone'] = 'Valid phone required'
        
        if not message or len(message) < 10:
            errors['message'] = 'Message must be at least 10 characters'
        
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400
        
        # Create quote request
        quote = QuoteRequest(
            name=name,
            email=email,
            phone=phone,
            service=service,
            message=message,
            location_id=location_id,
            camera_count=camera_count,
            resolution=resolution,
            difficulty_level=difficulty,
            estimated_price=estimated_price,
            ip_address=request.remote_addr,
            status='new'
        )
        
        db.session.add(quote)
        db.session.commit()
        
        current_app.logger.info(f"New quote request from {email}")
        
        # Send email to customer
        try:
            send_confirmation_email(quote)
        except Exception as e:
            current_app.logger.warning(f"Could not send email: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Quote request submitted successfully!',
            'quote_id': quote.id
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error submitting quote: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500

def send_confirmation_email(quote):
    """Send confirmation email to customer"""
    subject = f"CameraPro - Your Quote Request #{quote.id}"
    
    body = f"""
    Thank you for your quote request!
    
    Name: {quote.name}
    Email: {quote.email}
    Phone: {quote.phone}
    Service: {quote.service}
    
    Estimated Price: ${quote.estimated_price:,.2f}
    
    We will review your request and contact you within 24 hours.
    
    Best regards,
    CameraPro Team
    """
    
    msg = Message(subject=subject, recipients=[quote.email], body=body)
    mail.send(msg)

@contact_bp.route('/quotes', methods=['GET'])
def get_quotes():
    """Get all quote requests (admin only in production)"""
    quotes = QuoteRequest.query.order_by(QuoteRequest.created_at.desc()).all()
    return jsonify([q.to_dict() for q in quotes])

@contact_bp.route('/quotes/<int:quote_id>', methods=['GET'])
def get_quote(quote_id):
    """Get specific quote"""
    quote = QuoteRequest.query.get(quote_id)
    if not quote:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(quote.to_dict())

@contact_bp.route('/quotes/<int:quote_id>', methods=['PUT'])
def update_quote(quote_id):
    """Update quote status"""
    quote = QuoteRequest.query.get(quote_id)
    if not quote:
        return jsonify({'error': 'Not found'}), 404
    
    data = request.get_json()
    if 'status' in data:
        quote.status = data['status']
        db.session.commit()
    
    return jsonify(quote.to_dict())
