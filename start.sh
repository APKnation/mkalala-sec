#!/bin/bash

# Railway deployment script with explicit Python
echo "Starting deployment..."

# Use Python3 explicitly
python3 --version
pip3 --version

# Install requirements
pip3 install -r requirements.txt

# Run migrations
python3 manage.py migrate --noinput

# Collect static files
python3 manage.py collectstatic --noinput

# Start the application
exec gunicorn school_management.wsgi:application --bind 0.0.0.0:$PORT --workers 3
