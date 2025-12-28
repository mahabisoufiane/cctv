from flask import request, jsonify, current_app
from app.routes import api_bp
from app.models import Location, CameraSpecification, InstallationDifficulty
from app import db

@api_bp.route('/calculate-price', methods=['POST'])
def calculate_price():
    """
    Calculate price based on:
    - camera_count
    - resolution
    - location_id
    - difficulty_level
    """
    try:
        data = request.get_json()
        
        # Get values
        camera_count = int(data.get('camera_count', 0))
        resolution = data.get('resolution', '')
        location_id = int(data.get('location_id', 0))
        difficulty_level = data.get('difficulty_level', '')
        
        # Validate
        if not all([camera_count, resolution, location_id, difficulty_level]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get database records
        camera_spec = CameraSpecification.query.filter_by(resolution=resolution).first()
        location = Location.query.get(location_id)
        difficulty = InstallationDifficulty.query.filter_by(level=difficulty_level).first()
        
        if not all([camera_spec, location, difficulty]):
            return jsonify({'error': 'Invalid specifications'}), 400
        
        # Calculate price
        # Step 1: Base camera cost
        base_cost = camera_spec.base_price * camera_count
        
        # Step 2: Apply difficulty multiplier
        difficulty_adjusted = base_cost * difficulty.cost_multiplier
        
        # Step 3: Apply location multiplier
        location_adjusted = difficulty_adjusted * location.difficulty_multiplier
        
        # Step 4: Labor cost
        labor_cost = difficulty.hours_required * 50  # $50 per hour
        
        # Step 5: Total
        total_price = location_adjusted + labor_cost + location.travel_fee
        
        return jsonify({
            'base_cost': round(base_cost, 2),
            'difficulty_multiplier': difficulty.cost_multiplier,
            'location_multiplier': location.difficulty_multiplier,
            'labor_cost': round(labor_cost, 2),
            'travel_fee': location.travel_fee,
            'total_price': round(total_price, 2),
            'breakdown': {
                'camera_cost': round(location_adjusted, 2),
                'labor_cost': round(labor_cost, 2),
                'travel_fee': location.travel_fee
            }
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Price calculation error: {e}")
        return jsonify({'error': 'Server error'}), 500

@api_bp.route('/locations', methods=['GET'])
def get_locations():
    """Get all locations"""
    locations = Location.query.all()
    return jsonify([l.to_dict() for l in locations])

@api_bp.route('/resolutions', methods=['GET'])
def get_resolutions():
    """Get all camera resolutions"""
    resolutions = CameraSpecification.query.all()
    return jsonify([r.to_dict() for r in resolutions])

@api_bp.route('/difficulties', methods=['GET'])
def get_difficulties():
    """Get all difficulty levels"""
    difficulties = InstallationDifficulty.query.all()
    return jsonify([d.to_dict() for d in difficulties])
