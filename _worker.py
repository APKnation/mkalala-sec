#!/usr/bin/env python3
"""
Cloudflare Pages Functions for Django deployment
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')

# Initialize Django
import django
django.setup()

from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse
from django.urls import path, include
from django.conf import settings

# Django WSGI application
application = get_wsgi_application()

# Cloudflare Pages function handler
def handler(request):
    """
    Main handler for Cloudflare Pages Functions
    """
    # Convert Cloudflare request to Django request
    django_request = request

    # Process through Django
    response = application(django_request)

    return response

# URL patterns for Cloudflare Pages
urlpatterns = [
    path('', handler),
    path('admin/', handler),
    path('api/', handler),
]
