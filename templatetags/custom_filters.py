from django import template
from django.templatetags.static import static
import os

@register.filter
def image_exists(image_path):
    """Check if an image file exists in static folder"""
    try:
        # Try to get the static file path
        static_path = static(image_path)
        # Remove the static URL part to get relative path
        if static_path.startswith('/static/'):
            relative_path = static_path[7:]  # Remove '/static/'
        else:
            relative_path = image_path
            
        # Check if file exists in static directory
        full_path = os.path.join('static/images', os.path.basename(relative_path))
        return os.path.exists(full_path)
    except:
        return False

@register.filter  
def image_with_fallback(image_path, fallback_text='', fallback_color='bg-gray-300'):
    """Return image with fallback if it doesn't exist"""
    if image_exists(image_path):
        return image_path
    else:
        # Return a CSS class for fallback styling
        return f"class='{fallback_color}' data-fallback-text='{fallback_text}'"
