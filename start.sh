#!/bin/bash

# Install requirements first
echo "Installing requirements..."
pip install -r requirements.txt

# Ensure gunicorn is installed
echo "Ensuring gunicorn is installed..."
pip install gunicorn>=21.2.0

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start gunicorn
echo "Starting gunicorn..."
exec gunicorn school_management.wsgi:application --bind 0.0.0.0:$PORT --workers 3
