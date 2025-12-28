from flask import jsonify, render_template, request, current_app, g
from app.routes import admin_bp
from app.models import QuoteRequest, Location
from app.models_extended import Technician, Installation, Payment, Invoice
from app import db
from datetime import datetime, timedelta
import json

# Admin authentication decorator (basic example)
def require_admin(f):
    def decorated(*args, **kwargs):
        # TODO: Implement proper JWT/session-based auth
        admin_key = request.headers.get('X-Admin-Key')
        if admin_key != current_app.config.get('ADMIN_API_KEY'):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated


# ============================================================================
# DASHBOARD ROUTES
# ============================================================================

@admin_bp.route('/dashboard')
def dashboard():
    """Admin dashboard homepage"""
    return render_template('admin/dashboard.html')


@admin_bp.route('/api/dashboard/stats')
def dashboard_stats():
    """Get dashboard statistics"""
    try:
        today = datetime.utcnow().date()
        month_start = today.replace(day=1)
        year_start = today.replace(month=1, day=1)
        
        # Quote statistics
        total_quotes = QuoteRequest.query.count()
        new_quotes = QuoteRequest.query.filter(
            QuoteRequest.created_at >= datetime.utcnow() - timedelta(days=7),
            QuoteRequest.status == 'new'
        ).count()
        converted_quotes = QuoteRequest.query.filter_by(status='converted').count()
        conversion_rate = (converted_quotes / total_quotes * 100) if total_quotes > 0 else 0
        
        # Revenue statistics
        month_revenue = db.session.query(db.func.sum(Invoice.total_amount)).filter(
            Invoice.issued_date >= month_start,
            Invoice.status.in_(['paid', 'issued'])
        ).scalar() or 0
        
        year_revenue = db.session.query(db.func.sum(Invoice.total_amount)).filter(
            Invoice.issued_date >= year_start,
            Invoice.status.in_(['paid', 'issued'])
        ).scalar() or 0
        
        # Installation statistics
        completed_installations = Installation.query.filter_by(status='completed').count()
        pending_installations = Installation.query.filter_by(status='pending').count()
        in_progress = Installation.query.filter_by(status='in-progress').count()
        
        # Technician statistics
        available_technicians = Technician.query.filter_by(status='available').count()
        busy_technicians = Technician.query.filter_by(status='busy').count()
        
        return jsonify({
            'success': True,
            'quotes': {
                'total': total_quotes,
                'new': new_quotes,
                'converted': converted_quotes,
                'conversion_rate': round(conversion_rate, 2)
            },
            'revenue': {
                'this_month': round(month_revenue, 2),
                'this_year': round(year_revenue, 2),
                'currency': 'MAD'
            },
            'installations': {
                'completed': completed_installations,
                'pending': pending_installations,
                'in_progress': in_progress
            },
            'team': {
                'available': available_technicians,
                'busy': busy_technicians,
                'total': Technician.query.count()
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Dashboard stats error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# QUOTE MANAGEMENT ROUTES
# ============================================================================

@admin_bp.route('/api/quotes')
def list_quotes():
    """Get all quotes with filtering"""
    try:
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = QuoteRequest.query
        
        if status:
            query = query.filter_by(status=status)
        
        quotes = query.order_by(QuoteRequest.created_at.desc()).paginate(
            page=page, per_page=per_page
        )
        
        return jsonify({
            'success': True,
            'total': quotes.total,
            'pages': quotes.pages,
            'current_page': page,
            'data': [q.to_dict() for q in quotes.items]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/quotes/<int:quote_id>')
def get_quote_detail(quote_id):
    """Get quote details with related data"""
    try:
        quote = QuoteRequest.query.get(quote_id)
        if not quote:
            return jsonify({'success': False, 'error': 'Quote not found'}), 404
        
        installation = Installation.query.filter_by(quote_id=quote_id).first()
        payment = Payment.query.filter_by(quote_id=quote_id).first()
        invoice = Invoice.query.filter_by(quote_id=quote_id).first()
        
        return jsonify({
            'success': True,
            'quote': quote.to_dict(),
            'installation': installation.to_dict() if installation else None,
            'payment': payment.to_dict() if payment else None,
            'invoice': invoice.to_dict() if invoice else None
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/quotes/<int:quote_id>/assign-technician', methods=['POST'])
def assign_technician(quote_id):
    """Assign technician to a quote"""
    try:
        data = request.get_json()
        technician_id = data.get('technician_id')
        scheduled_date = data.get('scheduled_date')
        
        quote = QuoteRequest.query.get(quote_id)
        if not quote:
            return jsonify({'success': False, 'error': 'Quote not found'}), 404
        
        technician = Technician.query.get(technician_id)
        if not technician:
            return jsonify({'success': False, 'error': 'Technician not found'}), 404
        
        # Create or update installation
        installation = Installation.query.filter_by(quote_id=quote_id).first()
        if not installation:
            installation = Installation(quote_id=quote_id)
            db.session.add(installation)
        
        installation.technician_id = technician_id
        installation.scheduled_date = datetime.fromisoformat(scheduled_date)
        installation.status = 'pending'
        
        quote.status = 'contacted'
        technician.current_jobs += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Assigned to {technician.name}',
            'installation': installation.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# INSTALLATION MANAGEMENT ROUTES
# ============================================================================

@admin_bp.route('/api/installations')
def list_installations():
    """Get all installations"""
    try:
        status = request.args.get('status')
        technician_id = request.args.get('technician_id', type=int)
        page = request.args.get('page', 1, type=int)
        
        query = Installation.query
        
        if status:
            query = query.filter_by(status=status)
        if technician_id:
            query = query.filter_by(technician_id=technician_id)
        
        installations = query.order_by(Installation.scheduled_date.asc()).paginate(
            page=page, per_page=20
        )
        
        return jsonify({
            'success': True,
            'total': installations.total,
            'data': [i.to_dict() for i in installations.items]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/installations/<int:installation_id>/complete', methods=['POST'])
def complete_installation(installation_id):
    """Mark installation as complete"""
    try:
        data = request.get_json()
        installation = Installation.query.get(installation_id)
        if not installation:
            return jsonify({'success': False, 'error': 'Installation not found'}), 404
        
        installation.status = 'completed'
        installation.completion_date = datetime.utcnow()
        installation.labor_hours_actual = data.get('labor_hours_actual')
        installation.customer_satisfaction = data.get('satisfaction', 5)
        installation.notes = data.get('notes')
        
        quote = installation.quote
        quote.status = 'converted'
        
        if installation.technician:
            installation.technician.current_jobs = max(0, installation.technician.current_jobs - 1)
            installation.technician.total_completed += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Installation completed',
            'installation': installation.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# PAYMENT MANAGEMENT ROUTES
# ============================================================================

@admin_bp.route('/api/payments')
def list_payments():
    """Get all payments"""
    try:
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        
        query = Payment.query
        if status:
            query = query.filter_by(status=status)
        
        payments = query.order_by(Payment.created_at.desc()).paginate(
            page=page, per_page=20
        )
        
        return jsonify({
            'success': True,
            'total': payments.total,
            'data': [p.to_dict() for p in payments.items]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/payments/<int:quote_id>/create', methods=['POST'])
def create_payment(quote_id):
    """Create payment record for quote"""
    try:
        quote = QuoteRequest.query.get(quote_id)
        if not quote:
            return jsonify({'success': False, 'error': 'Quote not found'}), 404
        
        data = request.get_json()
        
        payment = Payment(
            quote_id=quote_id,
            amount=data.get('amount', 0),
            payment_method=data.get('payment_method', 'pending'),
            payment_gateway=data.get('payment_gateway', 'manual'),
            due_date=datetime.utcnow() + timedelta(days=30)
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Payment created',
            'payment': payment.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/payments/<int:payment_id>/mark-paid', methods=['POST'])
def mark_payment_paid(payment_id):
    """Mark payment as completed"""
    try:
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'success': False, 'error': 'Payment not found'}), 404
        
        payment.status = 'completed'
        payment.paid_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Payment marked as completed',
            'payment': payment.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# INVOICE MANAGEMENT ROUTES
# ============================================================================

@admin_bp.route('/api/invoices')
def list_invoices():
    """Get all invoices"""
    try:
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        
        query = Invoice.query
        if status:
            query = query.filter_by(status=status)
        
        invoices = query.order_by(Invoice.issued_date.desc()).paginate(
            page=page, per_page=20
        )
        
        return jsonify({
            'success': True,
            'total': invoices.total,
            'data': [i.to_dict() for i in invoices.items]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/invoices/<int:quote_id>/generate', methods=['POST'])
def generate_invoice(quote_id):
    """Generate invoice from quote"""
    try:
        quote = QuoteRequest.query.get(quote_id)
        if not quote:
            return jsonify({'success': False, 'error': 'Quote not found'}), 404
        
        data = request.get_json()
        
        # Create invoice
        invoice = Invoice(
            quote_id=quote_id,
            subtotal=data.get('subtotal', 0),
            tax_amount=data.get('tax_amount', 0),
            total_amount=data.get('total_amount', 0),
            due_date=datetime.utcnow() + timedelta(days=30),
            notes=data.get('notes', '')
        )
        
        invoice.invoice_number = invoice.generate_invoice_number()
        invoice.status = 'issued'
        
        db.session.add(invoice)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Invoice {invoice.invoice_number} generated',
            'invoice': invoice.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# TECHNICIAN MANAGEMENT ROUTES
# ============================================================================

@admin_bp.route('/api/technicians')
def list_technicians():
    """Get all technicians"""
    try:
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        
        query = Technician.query
        if status:
            query = query.filter_by(status=status)
        
        technicians = query.order_by(Technician.name).paginate(
            page=page, per_page=20
        )
        
        return jsonify({
            'success': True,
            'total': technicians.total,
            'data': [t.to_dict() for t in technicians.items]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/technicians', methods=['POST'])
def create_technician():
    """Create new technician"""
    try:
        data = request.get_json()
        
        technician = Technician(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            specialization=data.get('specialization'),
            salary=data.get('salary', 0)
        )
        
        db.session.add(technician)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Technician created',
            'technician': technician.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/technicians/<int:technician_id>', methods=['PUT'])
def update_technician(technician_id):
    """Update technician"""
    try:
        technician = Technician.query.get(technician_id)
        if not technician:
            return jsonify({'success': False, 'error': 'Technician not found'}), 404
        
        data = request.get_json()
        
        if 'status' in data:
            technician.status = data['status']
        if 'specialization' in data:
            technician.specialization = data['specialization']
        if 'salary' in data:
            technician.salary = data['salary']
        
        technician.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Technician updated',
            'technician': technician.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
