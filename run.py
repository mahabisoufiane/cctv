import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import create_app, db
from app.models import Location, CameraSpecification, InstallationDifficulty, QuoteRequest

# Create Flask app
app = create_app(os.environ.get('FLASK_ENV', 'development'))

# For database operations in terminal
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Location': Location,
        'CameraSpecification': CameraSpecification,
        'InstallationDifficulty': InstallationDifficulty,
        'QuoteRequest': QuoteRequest
    }

# Initialize database with sample data
@app.cli.command()
def init_db():
    """Initialize database with pricing data"""
    print("Creating database tables...")
    
    # Drop existing tables (careful in production!)
    db.drop_all()
    db.create_all()
    
    # Add locations
    locations = [
        Location(name='Philadelphia', difficulty_multiplier=1.0, travel_fee=50),
        Location(name='Boston', difficulty_multiplier=1.1, travel_fee=80),
        Location(name='New York', difficulty_multiplier=1.2, travel_fee=100),
        Location(name='Remote/Rural', difficulty_multiplier=1.5, travel_fee=200),
    ]
    
    # Add camera specifications
    cameras = [
        CameraSpecification(resolution='1080p', base_price=150, description='Full HD'),
        CameraSpecification(resolution='2mp', base_price=200, description='HD+'),
        CameraSpecification(resolution='4mp', base_price=300, description='4K'),
        CameraSpecification(resolution='8mp', base_price=500, description='Ultra 4K'),
    ]
    
    # Add difficulty levels
    difficulties = [
        InstallationDifficulty(
            level='Easy',
            cost_multiplier=1.0,
            hours_required=4,
            description='Simple mounting, no extra wiring'
        ),
        InstallationDifficulty(
            level='Medium',
            cost_multiplier=1.3,
            hours_required=8,
            description='Standard installation with cabling'
        ),
        InstallationDifficulty(
            level='Hard',
            cost_multiplier=1.8,
            hours_required=16,
            description='Complex setup, extensive cabling, network config'
        ),
    ]
    
    # Add to database
    try:
        db.session.add_all(locations + cameras + difficulties)
        db.session.commit()
        
        print("✅ Database initialized successfully!")
        print(f"   ✓ Added {len(locations)} locations")
        print(f"   ✓ Added {len(cameras)} camera types")
        print(f"   ✓ Added {len(difficulties)} difficulty levels")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error initializing database: {e}")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
