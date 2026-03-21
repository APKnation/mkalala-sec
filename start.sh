#!/bin/bash

# Simple Railway deployment script
echo "Starting deployment..."

# Install requirements
pip install -r requirements.txt

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start the application
exec gunicorn school_management.wsgi:application --bind 0.0.0.0:$PORT --workers 3
