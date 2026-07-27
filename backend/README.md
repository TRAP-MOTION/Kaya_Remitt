# KayaRemit Backend

Flask REST API for KayaRemit. PostgreSQL is the supported database. Payments use PayChangu.

## Quick start

From the **repository root**:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with SECRET_KEY, DATABASE_URL, JWT_SECRET_KEY, PayChangu values
```

Then from the **repository root** (so `backend` is importable):

```bash
export PYTHONPATH=.
```

### Development

```bash
export FLASK_ENV=development
python backend/run.py
```

### Production (Gunicorn)

```bash
export FLASK_ENV=production
gunicorn -c backend/gunicorn.conf.py backend.wsgi:app
```

## Useful files

| File | Purpose |
|------|---------|
| `run.py` | Flask development server |
| `wsgi.py` | Gunicorn / WSGI entrypoint |
| `gunicorn.conf.py` | Production worker / bind settings |
| `.env.example` | Required environment variables |
| `api_reference.md` | HTTP API documentation |

Full project setup notes live in the root [`README.md`](../README.md).
