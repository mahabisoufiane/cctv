from flask import request, jsonify, current_app, g
from app.routes import contact_bp
from app.models import QuoteRequest
from app import db, mail
from flask_mail import Message
import re
from datetime import datetime

# Translation strings
TRANSLATIONS = {
    'ar': {
        'thank_you': 'شكراً لطلبك',
        'received': 'تم استقبال طلبك بنجاح',
        'error': 'حدث خطأ في المعالجة',
        'invalid_email': 'البريد الإلكتروني غير صحيح',
        'invalid_phone': 'رقم الهاتف غير صحيح',
        'invalid_name': 'الاسم غير صحيح',
        'invalid_message': 'الرسالة يجب أن تكون 10 أحرف على الأقل',
        'quote_id': 'رقم الطلب',
    },
    'fr': {
        'thank_you': 'Merci pour votre demande',
        'received': 'Votre demande a été reçue avec succès',
        'error': 'Une erreur s\'est produite lors du traitement',
        'invalid_email': 'E-mail invalide',
        'invalid_phone': 'Numéro de téléphone invalide',
        'invalid_name': 'Nom invalide',
        'invalid_message': 'Le message doit contenir au moins 10 caractères',
        'quote_id': 'ID de devis',
    },
    'en': {
        'thank_you': 'Thank you for your request',
        'received': 'Your request has been received successfully',
        'error': 'An error occurred during processing',
        'invalid_email': 'Invalid email address',
        'invalid_phone': 'Invalid phone number',
        'invalid_name': 'Invalid name',
        'invalid_message': 'Message must be at least 10 characters',
        'quote_id': 'Quote ID',
    }
}


def get_translation(lang: str, key: str) -> str:
    """Get translated string"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['ar']).get(key, key)


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone format (flexible for international formats)"""
    # Remove spaces, dashes, parentheses
    clean = re.sub(r'[\s\-\(\)\+]', '', phone)
    # Should be only numbers
    return clean.isdigit() and len(clean) >= 8


@contact_bp.route('/quote', methods=['POST', 'OPTIONS'])
def submit_quote():
    """Handle quote request submission"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json() or {}
        lang = g.get('current_lang', 'ar')
        
        # Extract form data
        name = (data.get('name') or '').strip()
        email = (data.get('email') or '').strip().lower()
        phone = (data.get('phone') or '').strip()
        service = (data.get('service') or '').strip()
        message = (data.get('message') or '').strip()
        location_id = data.get('location_id')
        camera_count = data.get('camera_count')
        resolution = data.get('resolution')
        difficulty = data.get('difficulty_level')
        estimated_price = data.get('estimated_price')
        
        # Validate
        errors = {}
        
        if not name or len(name) < 2 or len(name) > 100:
            errors['name'] = get_translation(lang, 'invalid_name')
        
        if not email or not validate_email(email):
            errors['email'] = get_translation(lang, 'invalid_email')
        
        if not phone or not validate_phone(phone):
            errors['phone'] = get_translation(lang, 'invalid_phone')
        
        if not message or len(message) < 10:
            errors['message'] = get_translation(lang, 'invalid_message')
        
        if errors:
            return jsonify({
                'success': False,
                'errors': errors,
                'language': lang
            }), 400
        
        # Create quote request
        quote = QuoteRequest(
            name=name,
            email=email,
            phone=phone,
            service=service or 'General Inquiry',
            message=message,
            language=lang,
            location_id=location_id,
            camera_count=camera_count,
            resolution=resolution,
            difficulty_level=difficulty,
            estimated_price=estimated_price,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            status='new'
        )
        
        db.session.add(quote)
        db.session.commit()
        
        current_app.logger.info(f"New quote request #{quote.id} from {email}")
        
        # Send email to customer
        try:
            send_confirmation_email(quote, lang)
        except Exception as e:
            current_app.logger.warning(f"Could not send confirmation email: {e}")
        
        # Send notification to admin
        try:
            send_admin_notification(quote, lang)
        except Exception as e:
            current_app.logger.warning(f"Could not send admin notification: {e}")
        
        return jsonify({
            'success': True,
            'message': get_translation(lang, 'received'),
            'language': lang,
            'quote_id': quote.id,
            'quote_data': quote.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error submitting quote: {e}", exc_info=True)
        lang = g.get('current_lang', 'ar')
        return jsonify({
            'success': False,
            'error': get_translation(lang, 'error'),
            'message': str(e),
            'language': lang
        }), 500


def send_confirmation_email(quote: QuoteRequest, lang: str):
    """Send confirmation email to customer"""
    subject_text = {
        'ar': f'طلبك #{quote.id} - نظام الكاميرات الأمنية',
        'fr': f'Votre demande #{quote.id} - Système CCTV',
        'en': f'Your Request #{quote.id} - CCTV System'
    }
    
    body_text = {
        'ar': f"""مرحباً {quote.name},

شكراً لطلبك. تم استقبال طلب التثبيت الخاص بك برقم {quote.id}.

سيتم التواصل معك في أقرب وقت ممكن.

البريد الإلكتروني: {quote.email}
رقم الهاتف: {quote.phone}

مع تحياتنا،
فريق CCTV Pro
""",
        'fr': f"""Bonjour {quote.name},

Merci pour votre demande. Votre demande d'installation n°{quote.id} a été reçue.

Nous vous contacterons très bientôt.

E-mail : {quote.email}
Téléphone : {quote.phone}

Cordialement,
Équipe CCTV Pro
""",
        'en': f"""Hello {quote.name},

Thank you for your request. Your installation request ##{quote.id} has been received.

We will contact you as soon as possible.

Email: {quote.email}
Phone: {quote.phone}

Best regards,
CCTV Pro Team
"""
    }
    
    subject = subject_text.get(lang, subject_text['en'])
    body = body_text.get(lang, body_text['en'])
    
    msg = Message(
        subject=subject,
        recipients=[quote.email],
        body=body
    )
    mail.send(msg)


def send_admin_notification(quote: QuoteRequest, lang: str):
    """Send notification email to admin"""
    subject = f"New Quote Request #{quote.id} from {quote.name}"
    body = f"""New Quote Request Details:

ID: {quote.id}
Name: {quote.name}
Email: {quote.email}
Phone: {quote.phone}
Service: {quote.service}
Language: {lang}
Location: {quote.location_id}
Camera Count: {quote.camera_count}
Resolution: {quote.resolution}
Difficulty: {quote.difficulty_level}
Estimated Price: {quote.estimated_price} MAD
Message: {quote.message}
IP Address: {quote.ip_address}
Submitted: {quote.created_at}
"""
    
    admin_email = current_app.config.get('COMPANY_EMAIL')
    if admin_email:
        msg = Message(subject=subject, recipients=[admin_email], body=body)
        mail.send(msg)


@contact_bp.route('/quotes', methods=['GET'])
def get_quotes():
    """Get all quote requests (admin endpoint)"""
    try:
        quotes = QuoteRequest.query.order_by(QuoteRequest.created_at.desc()).all()
        return jsonify({
            'success': True,
            'count': len(quotes),
            'data': [q.to_dict() for q in quotes]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@contact_bp.route('/quotes/<int:quote_id>', methods=['GET'])
def get_quote(quote_id: int):
    """Get specific quote by ID"""
    try:
        quote = QuoteRequest.query.get(quote_id)
        if not quote:
            return jsonify({
                'success': False,
                'error': 'Quote not found'
            }), 404
        return jsonify({
            'success': True,
            'data': quote.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@contact_bp.route('/quotes/<int:quote_id>', methods=['PUT'])
def update_quote(quote_id: int):
    """Update quote status or notes"""
    try:
        quote = QuoteRequest.query.get(quote_id)
        if not quote:
            return jsonify({
                'success': False,
                'error': 'Quote not found'
            }), 404
        
        data = request.get_json() or {}
        
        if 'status' in data and data['status'] in ['new', 'contacted', 'converted', 'rejected']:
            quote.status = data['status']
        
        if 'notes' in data:
            quote.notes = data['notes']
        
        if 'followed_up_at' in data:
            quote.followed_up_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Quote updated',
            'data': quote.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
