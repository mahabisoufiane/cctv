from flask import jsonify, render_template, request, current_app, g
from app.routes import technician_bp
from app.models_extended import Technician, Installation
from app import db
from datetime import datetime
from functools import wraps

# Technician authentication
def require_technician(f):
    """Decorator to verify technician credentials"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # TODO: Implement JWT token validation
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'Missing authorization'}), 401
        return f(*args, **kwargs)
    return decorated


# ============================================================================
# DASHBOARD & JOBS
# ============================================================================

@technician_bp.route('/dashboard')
def technician_dashboard():
    """Technician dashboard"""
    return render_template('technician/dashboard.html')


@technician_bp.route('/api/jobs')
@require_technician
def list_jobs():
    """Get technician's active jobs"""
    try:
        # TODO: Get technician_id from JWT token
        technician_id = request.args.get('technician_id', type=int)
        status = request.args.get('status', 'pending')  # pending, in-progress, completed
        
        if not technician_id:
            return jsonify({'success': False, 'error': 'Technician ID required'}), 400
        
        technician = Technician.query.get(technician_id)
        if not technician:
            return jsonify({'success': False, 'error': 'Technician not found'}), 404
        
        query = Installation.query.filter_by(technician_id=technician_id)
        
        if status != 'all':
            query = query.filter_by(status=status)
        
        installations = query.order_by(
            Installation.scheduled_date.asc()
        ).all()
        
        return jsonify({
            'success': True,
            'technician': technician.to_dict(),
            'jobs': [{
                'id': i.id,
                'quote_id': i.quote_id,
                'status': i.status,
                'scheduled_date': i.scheduled_date.isoformat() if i.scheduled_date else None,
                'customer_name': i.quote.name,
                'customer_phone': i.quote.phone,
                'customer_email': i.quote.email,
                'location': i.quote.location_id,
                'camera_count': i.quote.camera_count,
                'notes': i.notes,
                'created_at': i.created_at.isoformat()
            } for i in installations]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Jobs list error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@technician_bp.route('/api/jobs/<int:installation_id>')
@require_technician
def get_job_detail(installation_id):
    """Get detailed job information"""
    try:
        installation = Installation.query.get(installation_id)
        if not installation:
            return jsonify({'success': False, 'error': 'Job not found'}), 404
        
        quote = installation.quote
        
        return jsonify({
            'success': True,
            'job': {
                'id': installation.id,
                'quote_id': installation.quote_id,
                'status': installation.status,
                'scheduled_date': installation.scheduled_date.isoformat() if installation.scheduled_date else None,
                'completion_date': installation.completion_date.isoformat() if installation.completion_date else None,
                'labor_hours_actual': installation.labor_hours_actual,
                'notes': installation.notes,
                'issues': installation.issues_encountered,
                'satisfaction': installation.customer_satisfaction
            },
            'customer': {
                'name': quote.name,
                'email': quote.email,
                'phone': quote.phone,
                'address': f"Location {quote.location_id}",  # TODO: Get actual address
            },
            'project': {
                'camera_count': quote.camera_count,
                'resolution': quote.resolution,
                'difficulty': quote.difficulty_level,
                'service': quote.service,
                'message': quote.message
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# JOB STATUS UPDATES
# ============================================================================

@technician_bp.route('/api/jobs/<int:installation_id>/start', methods=['POST'])
@require_technician
def start_job(installation_id):
    """Mark job as in-progress"""
    try:
        installation = Installation.query.get(installation_id)
        if not installation:
            return jsonify({'success': False, 'error': 'Job not found'}), 404
        
        if installation.status != 'pending':
            return jsonify({
                'success': False,
                'error': f"Cannot start job with status: {installation.status}"
            }), 400
        
        installation.status = 'in-progress'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Job started',
            'installation': installation.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@technician_bp.route('/api/jobs/<int:installation_id>/complete', methods=['POST'])
@require_technician
def complete_job(installation_id):
    """Mark job as complete with details"""
    try:
        data = request.get_json()
        installation = Installation.query.get(installation_id)
        if not installation:
            return jsonify({'success': False, 'error': 'Job not found'}), 404
        
        if installation.status != 'in-progress':
            return jsonify({
                'success': False,
                'error': f"Cannot complete job with status: {installation.status}"
            }), 400
        
        installation.status = 'completed'
        installation.completion_date = datetime.utcnow()
        installation.labor_hours_actual = data.get('labor_hours', 0)
        installation.issues_encountered = data.get('issues', '')
        installation.notes = data.get('notes', '')
        
        # Update technician stats
        if installation.technician:
            installation.technician.current_jobs = max(0, installation.technician.current_jobs - 1)
            installation.technician.total_completed += 1
        
        # Update quote status
        installation.quote.status = 'converted'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Job completed successfully',
            'installation': installation.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@technician_bp.route('/api/jobs/<int:installation_id>/issue', methods=['POST'])
@require_technician
def report_issue(installation_id):
    """Report issue with a job"""
    try:
        data = request.get_json()
        installation = Installation.query.get(installation_id)
        if not installation:
            return jsonify({'success': False, 'error': 'Job not found'}), 404
        
        installation.status = 'failed'
        installation.issues_encountered = data.get('issue_description', '')
        installation.notes = data.get('admin_notes', '')
        
        db.session.commit()
        
        # TODO: Send notification to admin
        
        return jsonify({
            'success': True,
            'message': 'Issue reported to admin',
            'installation': installation.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# PHOTO UPLOADS
# ============================================================================

@technician_bp.route('/api/jobs/<int:installation_id>/upload-photo', methods=['POST'])
@require_technician
def upload_photo(installation_id):
    """Upload installation photos"""
    try:
        from werkzeug.utils import secure_filename
        import os
        
        installation = Installation.query.get(installation_id)
        if not installation:
            return jsonify({'success': False, 'error': 'Job not found'}), 404
        
        if 'photo' not in request.files:
            return jsonify({'success': False, 'error': 'No photo provided'}), 400
        
        file = request.files['photo']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        
        # TODO: Implement file upload to cloud storage (AWS S3, etc.)
        # For now, return placeholder
        photo_url = f"https://storage.example.com/installations/{installation_id}/{file.filename}"
        
        # Store photo URLs in JSON array
        if not installation.photos_url:
            installation.photos_url = '[]'
        
        import json
        photos = json.loads(installation.photos_url)
        photos.append(photo_url)
        installation.photos_url = json.dumps(photos)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Photo uploaded',
            'url': photo_url
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


def allowed_file(filename):
    """Check if file is allowed"""
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================================================================
# CUSTOMER FEEDBACK
# ============================================================================

@technician_bp.route('/api/jobs/<int:installation_id>/feedback', methods=['POST'])
@require_technician
def submit_feedback(installation_id):
    """Submit customer feedback after installation"""
    try:
        data = request.get_json()
        installation = Installation.query.get(installation_id)
        if not installation:
            return jsonify({'success': False, 'error': 'Job not found'}), 404
        
        if installation.status != 'completed':
            return jsonify({
                'success': False,
                'error': 'Can only submit feedback for completed jobs'
            }), 400
        
        installation.customer_satisfaction = data.get('satisfaction', 5)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Feedback recorded',
            'satisfaction': installation.customer_satisfaction
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# PROFILE & STATS
# ============================================================================

@technician_bp.route('/api/technician/profile/<int:technician_id>')
@require_technician
def get_profile(technician_id):
    """Get technician profile"""
    try:
        technician = Technician.query.get(technician_id)
        if not technician:
            return jsonify({'success': False, 'error': 'Technician not found'}), 404
        
        completed_jobs = Installation.query.filter_by(
            technician_id=technician_id,
            status='completed'
        ).count()
        
        pending_jobs = Installation.query.filter_by(
            technician_id=technician_id,
            status='pending'
        ).count()
        
        in_progress_jobs = Installation.query.filter_by(
            technician_id=technician_id,
            status='in-progress'
        ).count()
        
        avg_satisfaction = db.session.query(
            db.func.avg(Installation.customer_satisfaction)
        ).filter_by(technician_id=technician_id).scalar() or 0
        
        return jsonify({
            'success': True,
            'profile': technician.to_dict(),
            'stats': {
                'completed_jobs': completed_jobs,
                'pending_jobs': pending_jobs,
                'in_progress_jobs': in_progress_jobs,
                'average_satisfaction': round(avg_satisfaction, 2),
                'current_jobs': technician.current_jobs,
                'total_completed': technician.total_completed,
                'rating': technician.rating
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@technician_bp.route('/api/technician/profile/<int:technician_id>', methods=['PUT'])
@require_technician
def update_profile(technician_id):
    """Update technician profile"""
    try:
        technician = Technician.query.get(technician_id)
        if not technician:
            return jsonify({'success': False, 'error': 'Technician not found'}), 404
        
        data = request.get_json()
        
        if 'phone' in data:
            technician.phone = data['phone']
        if 'specialization' in data:
            technician.specialization = data['specialization']
        
        technician.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated',
            'profile': technician.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
