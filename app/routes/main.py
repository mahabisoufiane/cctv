from flask import jsonify, render_template
from app.routes import main_bp
from app.models import Location, CameraSpecification, InstallationDifficulty

@main_bp.route('/')
def index():
    """Serve home page"""
    return render_template('index.html')

@main_bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'CameraPro API is running'
    })

@main_bp.route('/data')
def get_all_data():
    """Get all pricing data for frontend"""
    locations = Location.query.all()
    resolutions = CameraSpecification.query.all()
    difficulties = InstallationDifficulty.query.all()
    
    return jsonify({
        'locations': [l.to_dict() for l in locations],
        'resolutions': [r.to_dict() for r in resolutions],
        'difficulties': [d.to_dict() for d in difficulties]
    })
