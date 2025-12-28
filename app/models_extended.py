from app.models import Location, CameraSpecification, InstallationDifficulty, QuoteRequest
from datetime import datetime, timedelta
from app import db


class Technician(db.Model):
    """Technician profiles for field work"""
    __tablename__ = 'technician'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    specialization = db.Column(db.String(100))  # "Installation", "Maintenance", etc.
    status = db.Column(db.String(20), default='available')  # available, busy, off-duty
    current_jobs = db.Column(db.Integer, default=0)
    total_completed = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)  # 0-5 stars
    salary = db.Column(db.Float)  # Monthly salary
    hire_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    installations = db.relationship('Installation', backref='technician', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'specialization': self.specialization,
            'status': self.status,
            'current_jobs': self.current_jobs,
            'total_completed': self.total_completed,
            'rating': self.rating,
            'hire_date': self.hire_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }


class Installation(db.Model):
    """Track completed installations"""
    __tablename__ = 'installation'
    
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quote_request.id'), nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey('technician.id'))
    status = db.Column(db.String(20), default='pending')  # pending, in-progress, completed, failed
    scheduled_date = db.Column(db.DateTime)
    completion_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    photos_url = db.Column(db.String(500))  # JSON array of photo URLs
    labor_hours_actual = db.Column(db.Float)  # Actual hours spent
    issues_encountered = db.Column(db.Text)
    customer_satisfaction = db.Column(db.Integer)  # 1-5 rating
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quote = db.relationship('QuoteRequest', backref='installation')
    
    def to_dict(self):
        return {
            'id': self.id,
            'quote_id': self.quote_id,
            'technician_id': self.technician_id,
            'technician_name': self.technician.name if self.technician else None,
            'status': self.status,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'labor_hours_actual': self.labor_hours_actual,
            'customer_satisfaction': self.customer_satisfaction,
            'created_at': self.created_at.isoformat()
        }


class Payment(db.Model):
    """Payment records for quotes"""
    __tablename__ = 'payment'
    
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quote_request.id'), nullable=False, unique=True)
    amount = db.Column(db.Float, nullable=False)  # MAD
    currency = db.Column(db.String(3), default='MAD')
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed, refunded
    payment_method = db.Column(db.String(50))  # "credit_card", "bank_transfer", "cash"
    transaction_id = db.Column(db.String(200), unique=True)
    payment_gateway = db.Column(db.String(50))  # "stripe", "paypal", "maroc_telecom", "manual"
    paid_at = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)  # 30 days from quote
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quote = db.relationship('QuoteRequest', backref='payment')
    
    def to_dict(self):
        return {
            'id': self.id,
            'quote_id': self.quote_id,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'payment_method': self.payment_method,
            'payment_gateway': self.payment_gateway,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat()
        }


class Invoice(db.Model):
    """Invoice generation and tracking"""
    __tablename__ = 'invoice'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)  # INV-2026-00001
    quote_id = db.Column(db.Integer, db.ForeignKey('quote_request.id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'))
    issued_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)  # 30 days from issued
    status = db.Column(db.String(20), default='draft')  # draft, issued, paid, overdue, cancelled
    subtotal = db.Column(db.Float)  # Before tax
    tax_amount = db.Column(db.Float, default=0)  # VAT/TVA
    total_amount = db.Column(db.Float)  # MAD
    notes = db.Column(db.Text)
    pdf_url = db.Column(db.String(500))  # URL to generated PDF
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quote = db.relationship('QuoteRequest', backref='invoice')
    payment = db.relationship('Payment')
    
    def generate_invoice_number(self):
        """Generate sequential invoice number"""
        last_invoice = Invoice.query.order_by(Invoice.id.desc()).first()
        next_num = (last_invoice.id + 1) if last_invoice else 1
        year = datetime.utcnow().year
        return f"INV-{year}-{next_num:05d}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'quote_id': self.quote_id,
            'issued_date': self.issued_date.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'subtotal': self.subtotal,
            'tax_amount': self.tax_amount,
            'total_amount': self.total_amount,
            'pdf_url': self.pdf_url,
            'created_at': self.created_at.isoformat()
        }
