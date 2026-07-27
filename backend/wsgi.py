"""WSGI entrypoint for Gunicorn.

Usage (from the repository root):

    gunicorn -c backend/gunicorn.conf.py backend.wsgi:app

Or from the backend directory with PYTHONPATH set to the repo root:

    cd backend
    PYTHONPATH=.. gunicorn -c gunicorn.conf.py wsgi:app
"""
import os

from backend.app import create_app

# Prefer production when serving with Gunicorn; override with FLASK_ENV if needed.
app = create_app(os.getenv("FLASK_ENV", "production"))
