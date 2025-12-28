from flask import request, jsonify, current_app, g
from app.routes import api_bp
from app.models import Location, CameraSpecification, InstallationDifficulty
from app import db


@api_bp.route('/calculate-price', methods=['POST', 'OPTIONS'])
def calculate_price():
    """Calculate price based on specifications
    
    Expected JSON body:
    {
        "camera_count": 8,
        "resolution": "4mp",
        "location_id": 1,
        "difficulty_level": "Medium"
    }
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        lang = g.get('current_lang', 'ar')
        
        # Validate input
        camera_count = data.get('camera_count')
        resolution = data.get('resolution')
        location_id = data.get('location_id')
        difficulty_level = data.get('difficulty_level')
        
        if not all([camera_count, resolution, location_id, difficulty_level]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields',
                'required': ['camera_count', 'resolution', 'location_id', 'difficulty_level']
            }), 400
        
        try:
            camera_count = int(camera_count)
            location_id = int(location_id)
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Invalid data types',
                'details': 'camera_count and location_id must be integers'
            }), 400
        
        if camera_count <= 0 or camera_count > 100:
            return jsonify({
                'success': False,
                'error': 'Invalid camera count',
                'details': 'camera_count must be between 1 and 100'
            }), 400
        
        # Get database records
        camera_spec = CameraSpecification.query.filter_by(resolution=resolution).first()
        location = Location.query.get(location_id)
        difficulty = InstallationDifficulty.query.filter_by(level=difficulty_level).first()
        
        if not camera_spec:
            return jsonify({
                'success': False,
                'error': 'Invalid camera resolution',
                'available': [c.resolution for c in CameraSpecification.query.all()]
            }), 400
        
        if not location:
            return jsonify({
                'success': False,
                'error': 'Invalid location',
                'available_locations': [l.to_dict(lang) for l in Location.query.all()]
            }), 400
        
        if not difficulty:
            return jsonify({
                'success': False,
                'error': 'Invalid difficulty level',
                'available': [d.to_dict(lang) for d in InstallationDifficulty.query.all()]
            }), 400
        
        # Calculate price
        # Step 1: Base camera cost
        base_cost = camera_spec.base_price * camera_count
        
        # Step 2: Apply difficulty multiplier
        difficulty_adjusted = base_cost * difficulty.cost_multiplier
        
        # Step 3: Apply location multiplier
        location_adjusted = difficulty_adjusted * location.difficulty_multiplier
        
        # Step 4: Labor cost (250 MAD per hour)
        labor_cost = difficulty.hours_required * 250
        
        # Step 5: Total
        total_price = location_adjusted + labor_cost + location.travel_fee
        
        return jsonify({
            'success': True,
            'language': lang,
            'currency': 'MAD',
            'pricing': {
                'camera_model': camera_spec.get_description(lang),
                'camera_count': camera_count,
                'base_cost': round(base_cost, 2),
                'location': location.get_name(lang),
                'location_multiplier': location.difficulty_multiplier,
                'difficulty': difficulty.get_level(lang),
                'difficulty_multiplier': difficulty.cost_multiplier,
                'hours_required': difficulty.hours_required,
                'labor_rate': 250,
                'labor_cost': round(labor_cost, 2),
                'travel_fee': location.travel_fee,
                'subtotal': round(location_adjusted + labor_cost, 2),
                'travel_cost': location.travel_fee,
                'total_price': round(total_price, 2)
            },
            'breakdown': {
                'equipment': round(location_adjusted, 2),
                'labor': round(labor_cost, 2),
                'travel': location.travel_fee,
                'total': round(total_price, 2)
            }
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Price calculation error: {e}")
        return jsonify({
            'success': False,
            'error': 'Calculation error',
            'message': str(e)
        }), 500


@api_bp.route('/locations', methods=['GET'])
def get_locations():
    """Get all locations"""
    try:
        lang = g.get('current_lang', 'ar')
        locations = Location.query.all()
        return jsonify({
            'success': True,
            'language': lang,
            'data': [l.to_dict(lang) for l in locations]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/resolutions', methods=['GET'])
def get_resolutions():
    """Get all camera resolutions"""
    try:
        lang = g.get('current_lang', 'ar')
        resolutions = CameraSpecification.query.all()
        return jsonify({
            'success': True,
            'language': lang,
            'currency': 'MAD',
            'data': [r.to_dict(lang) for r in resolutions]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/difficulties', methods=['GET'])
def get_difficulties():
    """Get all difficulty levels"""
    try:
        lang = g.get('current_lang', 'ar')
        difficulties = InstallationDifficulty.query.all()
        return jsonify({
            'success': True,
            'language': lang,
            'data': [d.to_dict(lang) for d in difficulties]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
