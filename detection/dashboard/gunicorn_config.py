"""Gunicorn production config for deepfake detection dashboard."""

bind = "0.0.0.0:5050"
workers = 2
timeout = 120
accesslog = "-"
errorlog = "-"
loglevel = "info"
