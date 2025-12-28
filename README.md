# CCTV Pro - Professional Security Monitoring System

**Arabic/French/English | Morocco | Production Ready for 2026**

## Overview

CCTV Pro is an enterprise-grade security monitoring system designed for Moroccan businesses. The system provides:

- 🌍 **Multi-Language Support**: Arabic, French, English
- 💰 **Dynamic Pricing Calculator**: MAD currency with location-based multipliers
- 📊 **Professional Admin Dashboard**: Quote management and analytics
- 📧 **Email Notifications**: Automated confirmation and admin alerts
- 🔒 **Production Security**: CSRF protection, SQL injection prevention, input validation
- 📱 **Responsive Design**: Mobile-optimized interface
- ⚡ **Performance Optimized**: Database indexing, connection pooling

---

## Quick Start (5 Minutes)

### Prerequisites
- Python 3.9+
- PostgreSQL 12+ (or SQLite for testing)
- Git

### 1. Clone Repository
```bash
git clone https://github.com/mahabisoufiane/cctv.git
cd cctv
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment
```bash
cp .env.example .env
# Edit .env with your settings:
# - DATABASE_URL
# - MAIL_SERVER credentials
# - SECRET_KEY
```

### 5. Initialize Database
```bash
flask init-db
```

### 6. Run Development Server
```bash
python run.py
```

Access at: **http://localhost:5000**

---

## API Endpoints

### Data Endpoints
- `GET /data` - Get all pricing data (locations, cameras, difficulties)
- `GET /api/locations` - List all locations
- `GET /api/resolutions` - List camera resolutions
- `GET /api/difficulties` - List installation difficulties

### Pricing
- `POST /api/calculate-price` - Calculate installation price
  ```json
  {
    "camera_count": 8,
    "resolution": "4mp",
    "location_id": 1,
    "difficulty_level": "Medium"
  }
  ```

### Quotes
- `POST /quote` - Submit quote request
- `GET /quotes` - List all quotes (admin)
- `GET /quotes/<id>` - Get specific quote
- `PUT /quotes/<id>` - Update quote status

---

## Multi-Language Support

### How It Works

1. **Frontend Language Switcher**: Click language buttons (العربية | Français | English)
2. **URL Parameter**: Add `?lang=ar|fr|en` to any URL
3. **Default**: Arabic (`ar`) is the default language

### Translation System

- **Database Models**: Each field has `_ar`, `_fr`, `_en` variants
- **API Responses**: Return localized text based on `?lang` parameter
- **Frontend**: JavaScript switches UI text and reloads data

### Adding New Strings

In `app/routes/contact.py`:
```python
TRANSLATIONS = {
    'ar': {'key': 'Arabic text'},
    'fr': {'key': 'French text'},
    'en': {'key': 'English text'}
}
```

---

## Database Schema

### Locations
```
id, name_ar, name_fr, name_en, difficulty_multiplier, travel_fee
```

### CameraSpecification
```
id, resolution, base_price, description_ar, description_fr, description_en
```

### InstallationDifficulty
```
id, level, level_ar, level_fr, cost_multiplier, hours_required, 
description_ar, description_fr, description_en
```

### QuoteRequest
```
id, name, email, phone, service, message, language,
location_id, camera_count, resolution, difficulty_level, estimated_price,
status (new|contacted|converted|rejected), created_at, updated_at
```

---

## Production Deployment

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

### Using Docker
```bash
docker-compose up -d
```

### Environment Variables for Production
```bash
FLASK_ENV=production
SECRET_KEY=<random-32-char-key>
DATABASE_URL=postgresql://user:pass@host:5432/cctv_prod
CORS_ORIGINS=https://cctvsystem.ma
MAIL_USERNAME=<production-email>
MAIL_PASSWORD=<app-password>
```

---

## Features

### ✅ Completed
- [x] Multi-language support (AR/FR/EN)
- [x] Dynamic pricing calculator
- [x] Quote request form
- [x] Email notifications
- [x] API endpoints
- [x] Database models
- [x] Error handling
- [x] Input validation

### 🔜 Coming Soon (2026)
- [ ] Admin dashboard
- [ ] Quote analytics
- [ ] Payment integration
- [ ] SMS notifications
- [ ] WhatsApp integration
- [ ] Mobile app

---

## Security

- ✅ CSRF protection (Flask-WTF)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ XSS protection (input validation)
- ✅ Email validation (regex + email-validator)
- ✅ Phone validation
- ✅ Rate limiting (ready to implement)
- ✅ HTTPS support (production)

---

## Troubleshooting

### Database Connection Error
```bash
# Make sure PostgreSQL is running
psql -U postgres

# Check .env DATABASE_URL
echo $DATABASE_URL
```

### Email Not Sending
```bash
# Verify Gmail App Password
# https://myaccount.google.com/apppasswords

# Test email in Python
python
>>> from app import create_app, mail
>>> app = create_app()
>>> with app.app_context():
>>>     print(app.config['MAIL_SERVER'])
```

### Port Already in Use
```bash
# Use different port
FLASK_PORT=5001 python run.py
```

---

## File Structure

```
cctv/
├── app/
│   ├── __init__.py           # Application factory
│   ├── models.py             # Database models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py           # Home routes
│   │   ├── api.py            # API endpoints
│   │   └── contact.py        # Quote & contact
│   └── templates/
│       └── index.html        # Frontend
├── config.py                 # Configuration
├── run.py                    # Development server
├── wsgi.py                   # Production WSGI
├── requirements.txt          # Dependencies
├── .env                      # Environment (dev)
├── .env.production           # Environment (prod)
└── README.md                 # This file
```

---

## Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Commit changes: `git commit -am 'Add feature'`
3. Push: `git push origin feature/my-feature`
4. Submit pull request

---

## License

MIT License - See LICENSE file

---

## Support

- 📧 Email: info@cctvsystem.ma
- 📞 Phone: +212 5XX XXX XXX
- 🏢 Address: Casablanca, Morocco

---

**Last Updated**: December 28, 2025  
**Version**: 1.0.0  
**Status**: Production Ready ✅
