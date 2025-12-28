from flask import render_template, request, jsonify, session, redirect, url_for, current_app
from app import db
from app.models import Location, Resolution, Difficulty, Quote
from functools import wraps

def require_access(f):
    """Decorator to check if user has access token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if access is granted in session
        if not session.get('access_granted'):
            # If trying to access any route, redirect to access page
            return redirect(url_for('access_page'))
        return f(*args, **kwargs)
    return decorated_function

def init_app(app):
    @app.route('/access')
    def access_page():
        """Page to enter access token"""
        # If already has access, redirect to home
        if session.get('access_granted'):
            return redirect(url_for('index'))
        return render_template('access.html')
    
    @app.route('/validate-access', methods=['POST'])
    def validate_access():
        """Validate the access token"""
        data = request.get_json()
        token = data.get('token', '').strip()
        
        # Get the correct token from config
        correct_token = current_app.config['ACCESS_TOKEN']
        
        if token == correct_token:
            session['access_granted'] = True
            session.permanent = True  # Make session last 30 days
            return jsonify({'success': True, 'message': 'Accès autorisé!'})
        else:
            return jsonify({'success': False, 'message': 'Token incorrect. Veuillez réessayer.'})
    
    @app.route('/')
    @require_access
    def index():
        return render_template('index.html')
    
    @app.route('/data')
    @require_access
    def get_data():
        lang = request.args.get('lang', 'fr')
        
        locations = Location.query.filter_by(lang=lang).all()
        resolutions = Resolution.query.filter_by(lang=lang).all()
        difficulties = Difficulty.query.filter_by(lang=lang).all()
        
        return jsonify({
            'locations': [l.to_dict() for l in locations],
            'resolutions': [r.to_dict() for r in resolutions],
            'difficulties': [d.to_dict() for d in difficulties]
        })
    
    @app.route('/api/calculate-price', methods=['POST'])
    @require_access
    def calculate_price():
        data = request.get_json()
        
        location = Location.query.get(data['location_id'])
        resolution = Resolution.query.filter_by(
            resolution=data['resolution'],
            lang=location.lang
        ).first()
        difficulty = Difficulty.query.filter_by(
            level=data['difficulty_level'],
            lang=location.lang
        ).first()
        
        if not all([location, resolution, difficulty]):
            return jsonify({'success': False, 'message': 'Invalid data'}), 400
        
        base_price = data['camera_count'] * resolution.price_per_camera
        location_cost = location.travel_cost
        difficulty_multiplier = difficulty.multiplier
        
        total_price = (base_price + location_cost) * difficulty_multiplier
        
        return jsonify({
            'success': True,
            'pricing': {
                'base_price': base_price,
                'location_cost': location_cost,
                'difficulty_multiplier': difficulty_multiplier,
                'total_price': total_price
            }
        })
    
    @app.route('/quote', methods=['POST'])
    @require_access
    def submit_quote():
        data = request.get_json()
        
        quote = Quote(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            message=data.get('message'),
            service=data.get('service', 'General Inquiry')
        )
        
        try:
            db.session.add(quote)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Votre demande a été envoyée avec succès!'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': 'Une erreur s\'est produite. Veuillez réessayer.'
            }), 500
    
    @app.route('/admin')
    @require_access
    def admin():
        return render_template('admin.html')
    
    @app.route('/technician')
    @require_access
    def technician():
        return render_template('technician.html')

init_app(current_app._get_current_object())