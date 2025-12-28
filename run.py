#!/usr/bin/env python
"""Application entry point"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app, db
from app.models import Location, CameraSpecification, InstallationDifficulty, QuoteRequest

# Create Flask app - NO ARGUMENTS!
app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Make objects available in flask shell"""
    return {
        'db': db,
        'Location': Location,
        'CameraSpecification': CameraSpecification,
        'InstallationDifficulty': InstallationDifficulty,
        'QuoteRequest': QuoteRequest
    }


@app.cli.command()
def init_db():
    """Initialize database with sample data"""
    try:
        print("🔄 Creating database tables...")
        db.drop_all()
        db.create_all()
        
        # Add locations for Morocco
        locations = [
            Location(
                name_ar='الدار البيضاء',
                name_fr='Casablanca',
                name_en='Casablanca',
                difficulty_multiplier=1.0,
                travel_fee=200
            ),
            Location(
                name_ar='الرباط',
                name_fr='Rabat',
                name_en='Rabat',
                difficulty_multiplier=1.05,
                travel_fee=250
            ),
            Location(
                name_ar='فاس',
                name_fr='Fès',
                name_en='Fez',
                difficulty_multiplier=1.1,
                travel_fee=300
            ),
            Location(
                name_ar='مراكش',
                name_fr='Marrakech',
                name_en='Marrakech',
                difficulty_multiplier=1.15,
                travel_fee=400
            ),
            Location(
                name_ar='المناطق النائية',
                name_fr='Zones Reculées',
                name_en='Remote Areas',
                difficulty_multiplier=1.5,
                travel_fee=600
            ),
        ]
        
        # Add camera specifications
        cameras = [
            CameraSpecification(
                resolution='1080p',
                base_price=1200,
                description_ar='كاميرا Full HD',
                description_fr='Caméra Full HD',
                description_en='Full HD Camera'
            ),
            CameraSpecification(
                resolution='2mp',
                base_price=1800,
                description_ar='كاميرا 2MP',
                description_fr='Caméra 2MP',
                description_en='2MP Camera'
            ),
            CameraSpecification(
                resolution='4mp',
                base_price=2500,
                description_ar='كاميرا 4MP',
                description_fr='Caméra 4MP',
                description_en='4MP Camera'
            ),
            CameraSpecification(
                resolution='8mp',
                base_price=4500,
                description_ar='كاميرا 8MP Ultra 4K',
                description_fr='Caméra 8MP Ultra 4K',
                description_en='8MP Ultra 4K Camera'
            ),
        ]
        
        # Add difficulty levels
        difficulties = [
            InstallationDifficulty(
                level='Easy',
                level_ar='سهل',
                level_fr='Facile',
                cost_multiplier=1.0,
                hours_required=4,
                description_ar='تثبيت بسيط بدون أسلاك إضافية',
                description_fr='Installation simple sans câblage supplémentaire',
                description_en='Simple mounting without extra wiring'
            ),
            InstallationDifficulty(
                level='Medium',
                level_ar='متوسط',
                level_fr='Moyen',
                cost_multiplier=1.3,
                hours_required=8,
                description_ar='تثبيت قياسي مع أسلاك',
                description_fr='Installation standard avec câblage',
                description_en='Standard installation with cabling'
            ),
            InstallationDifficulty(
                level='Hard',
                level_ar='صعب',
                level_fr='Difficile',
                cost_multiplier=1.8,
                hours_required=16,
                description_ar='إعداد معقد مع أسلاك موسعة وتكوين الشبكة',
                description_fr='Mise en place complexe avec câblage étendu et configuration réseau',
                description_en='Complex setup with extensive cabling and network config'
            ),
        ]
        
        # Add to database
        db.session.add_all(locations + cameras + difficulties)
        db.session.commit()
        
        print("\n✅ Database initialized successfully!")
        print(f"   ✓ Added {len(locations)} locations")
        print(f"   ✓ Added {len(cameras)} camera types")
        print(f"   ✓ Added {len(difficulties)} difficulty levels")
        print("\n🎉 Ready to start the application!")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error initializing database: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    app.run(
        host=os.environ.get('FLASK_HOST', '127.0.0.1'),
        port=int(os.environ.get('FLASK_PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
