from app import db
from datetime import datetime
from flask import g


class Location(db.Model):
    """Installation locations with pricing multipliers and multi-language support"""
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(100), nullable=False)  # Arabic
    name_fr = db.Column(db.String(100), nullable=False)  # French
    name_en = db.Column(db.String(100), nullable=False)  # English
    difficulty_multiplier = db.Column(db.Float, default=1.0)
    travel_fee = db.Column(db.Float, default=0)  # MAD
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    quotes = db.relationship('QuoteRequest', backref='location_info', lazy=True, cascade='all, delete-orphan')

    def get_name(self, lang: str = None) -> str:
        """Get location name in specified language"""
        lang = lang or getattr(g, 'current_lang', 'ar')
        names = {'ar': self.name_ar, 'fr': self.name_fr, 'en': self.name_en}
        return names.get(lang, self.name_ar)

    def to_dict(self, lang: str = None) -> dict:
        """Serialize to dictionary with multi-language support"""
        lang = lang or getattr(g, 'current_lang', 'ar')
        return {
            'id': self.id,
            'name': self.get_name(lang),
            'difficulty_multiplier': self.difficulty_multiplier,
            'travel_fee': self.travel_fee,
            'language': lang
        }

    def __repr__(self):
        return f'<Location {self.name_en}>'


class CameraSpecification(db.Model):
    """Camera types with pricing and multi-language descriptions"""
    __tablename__ = 'camera_specifications'

    id = db.Column(db.Integer, primary_key=True)
    resolution = db.Column(db.String(50), unique=True, nullable=False)  # e.g., '1080p', '2mp', '4mp', '8mp'
    base_price = db.Column(db.Float, nullable=False)  # MAD
    description_ar = db.Column(db.String(255), nullable=False)
    description_fr = db.Column(db.String(255), nullable=False)
    description_en = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_description(self, lang: str = None) -> str:
        """Get description in specified language"""
        lang = lang or getattr(g, 'current_lang', 'ar')
        descriptions = {
            'ar': self.description_ar,
            'fr': self.description_fr,
            'en': self.description_en
        }
        return descriptions.get(lang, self.description_ar)

    def to_dict(self, lang: str = None) -> dict:
        """Serialize to dictionary with multi-language support"""
        lang = lang or getattr(g, 'current_lang', 'ar')
        return {
            'id': self.id,
            'resolution': self.resolution,
            'base_price': self.base_price,
            'description': self.get_description(lang),
            'currency': 'MAD',
            'language': lang
        }

    def __repr__(self):
        return f'<Camera {self.resolution}>'


class InstallationDifficulty(db.Model):
    """Installation difficulty levels with multi-language support"""
    __tablename__ = 'installation_difficulties'

    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(50), unique=True, nullable=False)  # e.g., 'Easy', 'Medium', 'Hard'
    level_ar = db.Column(db.String(50), nullable=False)  # Arabic level name
    level_fr = db.Column(db.String(50), nullable=False)  # French level name
    cost_multiplier = db.Column(db.Float, default=1.0)
    hours_required = db.Column(db.Float)
    description_ar = db.Column(db.String(255), nullable=False)
    description_fr = db.Column(db.String(255), nullable=False)
    description_en = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_level(self, lang: str = None) -> str:
        """Get level name in specified language"""
        lang = lang or getattr(g, 'current_lang', 'ar')
        levels = {'ar': self.level_ar, 'fr': self.level_fr, 'en': self.level}
        return levels.get(lang, self.level_ar)

    def get_description(self, lang: str = None) -> str:
        """Get description in specified language"""
        lang = lang or getattr(g, 'current_lang', 'ar')
        descriptions = {
            'ar': self.description_ar,
            'fr': self.description_fr,
            'en': self.description_en
        }
        return descriptions.get(lang, self.description_ar)

    def to_dict(self, lang: str = None) -> dict:
        """Serialize to dictionary with multi-language support"""
        lang = lang or getattr(g, 'current_lang', 'ar')
        return {
            'id': self.id,
            'level': self.get_level(lang),
            'cost_multiplier': self.cost_multiplier,
            'hours_required': self.hours_required,
            'description': self.get_description(lang),
            'language': lang
        }

    def __repr__(self):
        return f'<Difficulty {self.level}>'


class QuoteRequest(db.Model):
    """Customer quote requests from contact form"""
    __tablename__ = 'quote_requests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    service = db.Column(db.String(100), nullable=False)  # e.g., 'CCTV Installation', 'Maintenance', 'Consultation'
    message = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(5), default='ar')  # Language of request

    # Pricing details
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True)
    camera_count = db.Column(db.Integer, nullable=True)
    resolution = db.Column(db.String(50), nullable=True)  # e.g., '4mp'
    difficulty_level = db.Column(db.String(50), nullable=True)  # e.g., 'Medium'
    estimated_price = db.Column(db.Float, nullable=True)  # MAD

    # Metadata
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='new')  # new, contacted, converted, rejected
    notes = db.Column(db.Text, nullable=True)  # Internal notes
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    followed_up_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'service': self.service,
            'message': self.message,
            'language': self.language,
            'location_id': self.location_id,
            'camera_count': self.camera_count,
            'resolution': self.resolution,
            'difficulty_level': self.difficulty_level,
            'estimated_price': self.estimated_price,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'currency': 'MAD'
        }

    def __repr__(self):
        return f'<QuoteRequest {self.id} - {self.email}>'


class Admin(db.Model):
    """Admin users for dashboard access"""
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default='user')  # admin, manager, user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Admin {self.email}>'
