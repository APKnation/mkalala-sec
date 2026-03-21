#!/bin/bash

# Railway deployment script with Python 3.10
echo "Starting deployment..."

# Use Python explicitly
python --version
pip --version

# Install requirements
pip install -r requirements.txt

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start the application
exec gunicorn school_management.wsgi:application --bind 0.0.0.0:$PORT --workers 3
