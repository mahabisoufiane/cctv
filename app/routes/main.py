from flask import jsonify, render_template, g
from app.routes import main_bp
from app.models import Location, CameraSpecification, InstallationDifficulty


@main_bp.route('/')
@main_bp.route('/index')
def index():
    """Serve home page"""
    return render_template('index.html')


@main_bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'CCTV System API is running',
        'version': '1.0.0',
        'environment': 'production'
    }), 200


@main_bp.route('/data')
def get_all_data():
    """Get all pricing data for frontend in current language"""
    try:
        lang = g.get('current_lang', 'ar')
        
        locations = Location.query.all()
        resolutions = CameraSpecification.query.all()
        difficulties = InstallationDifficulty.query.all()
        
        return jsonify({
            'success': True,
            'language': lang,
            'currency': 'MAD',
            'locations': [l.to_dict(lang) for l in locations],
            'resolutions': [r.to_dict(lang) for r in resolutions],
            'difficulties': [d.to_dict(lang) for d in difficulties],
            'company': {
                'name': 'CCTV Pro',
                'phone': '+212 5XX XXX XXX',
                'email': 'info@cctvsystem.ma',
                'address': 'Casablanca, Morocco'
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch data',
            'message': str(e)
        }), 500
