"""Gunicorn configuration for the KayaRemit backend.

Environment variables:
  PORT          Bind port (default: 8000)
  HOST          Bind host (default: 0.0.0.0)
  WEB_CONCURRENCY  Number of worker processes (default: 2–4× CPU count capped)
  GUNICORN_TIMEOUT Request timeout in seconds (default: 120)
  GUNICORN_LOG_LEVEL  Log level (default: info)
"""
import multiprocessing
import os


def _default_workers() -> int:
    # Soft cap keeps sandbox / small VPS deployments light.
    return min(multiprocessing.cpu_count() * 2 + 1, 4)


bind = f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '8000')}"
workers = int(os.getenv("WEB_CONCURRENCY", _default_workers()))
worker_class = "sync"
threads = int(os.getenv("GUNICORN_THREADS", "1"))
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "30"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "5"))
preload_app = True
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
capture_output = True
