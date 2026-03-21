#!/bin/bash

# Set environment variables
export PYTHONPATH=$PYTHONPATH:/app
export DJANGO_SETTINGS_MODULE=school_management.settings

# Install system dependencies if needed
echo "Setting up environment..."
apt-get update && apt-get install -y build-essential libpq-dev || echo "System packages already installed"

# Install requirements
echo "Installing Python requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# Ensure gunicorn is available
echo "Ensuring gunicorn is installed..."
pip install gunicorn>=21.2.0

# Run Django migrations
echo "Running Django migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start gunicorn
echo "Starting gunicorn on port $PORT..."
exec gunicorn school_management.wsgi:application --bind 0.0.0.0:$PORT --workers 3
