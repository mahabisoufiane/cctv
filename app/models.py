from app import db
from datetime import datetime

class Location(db.Model):
    """Installation locations with pricing multipliers"""
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    difficulty_multiplier = db.Column(db.Float, default=1.0)
    travel_fee = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    quotes = db.relationship('QuoteRequest', backref='location_info', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'difficulty_multiplier': self.difficulty_multiplier,
            'travel_fee': self.travel_fee
        }

class CameraSpecification(db.Model):
    """Camera types with base prices"""
    __tablename__ = 'camera_specifications'
    
    id = db.Column(db.Integer, primary_key=True)
    resolution = db.Column(db.String(50), unique=True, nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'resolution': self.resolution,
            'base_price': self.base_price,
            'description': self.description
        }

class InstallationDifficulty(db.Model):
    """Installation difficulty levels"""
    __tablename__ = 'installation_difficulties'
    
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(50), unique=True, nullable=False)
    cost_multiplier = db.Column(db.Float, default=1.0)
    hours_required = db.Column(db.Float)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'level': self.level,
            'cost_multiplier': self.cost_multiplier,
            'hours_required': self.hours_required,
            'description': self.description
        }

class QuoteRequest(db.Model):
    """Customer quote requests from contact form"""
    __tablename__ = 'quote_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    service = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Pricing details
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    camera_count = db.Column(db.Integer)
    resolution = db.Column(db.String(50))
    difficulty_level = db.Column(db.String(50))
    estimated_price = db.Column(db.Float)
    
    # Metadata
    ip_address = db.Column(db.String(50))
    status = db.Column(db.String(20), default='new')  # new, contacted, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'service': self.service,
            'message': self.message,
            'camera_count': self.camera_count,
            'resolution': self.resolution,
            'difficulty_level': self.difficulty_level,
            'estimated_price': self.estimated_price,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
