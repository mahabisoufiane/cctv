#!/usr/bin/env python
"""WSGI entry point for production servers (Gunicorn, uWSGI, etc.)"""
import os
from dotenv import load_dotenv

load_dotenv('.env.production')

from app import create_app, db

app = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == '__main__':
    app.run()
