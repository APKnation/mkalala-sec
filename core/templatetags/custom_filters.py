from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def image_with_fallback(image_path, alt_text="", fallback_class=""):
    """Return image src with fallback class - enhanced with error handling"""
    if not image_path:
        return mark_safe(f'alt="{alt_text}" class="{fallback_class}"')
    
    if not alt_text:
        alt_text = "Image"
    
    if not fallback_class:
        fallback_class = "bg-gray-300"
    
    # Ensure the image path doesn't start with static/
    if image_path.startswith('static/'):
        image_path = image_path[7:]
    elif image_path.startswith('/static/'):
        image_path = image_path[8:]
    
    # Add JavaScript fallback for missing images
    fallback_js = f"onerror=\"this.className='{fallback_class}'; this.alt='{alt_text}'; this.style.display='block'; this.style.height='200px';\""
    
    return mark_safe(f'src="/static/{image_path}" alt="{alt_text}" class="{fallback_class}" {fallback_js}')

@register.simple_tag
def img_tag(image_path, alt_text="", fallback_class="", extra_classes=""):
    """Generate complete img tag with fallback - alternative approach"""
    if not image_path:
        return mark_safe(f'<div class="{fallback_class} {extra_classes}">{alt_text}</div>')
    
    if not alt_text:
        alt_text = "Image"
    
    if not fallback_class:
        fallback_class = "bg-gray-300"
    
    # Clean image path
    if image_path.startswith('static/'):
        image_path = image_path[7:]
    elif image_path.startswith('/static/'):
        image_path = image_path[8:]
    
    return mark_safe(f'<img src="/static/{image_path}" alt="{alt_text}" class="{fallback_class} {extra_classes}" onerror="this.className=\'{fallback_class} {extra_classes}\'; this.alt=\'{alt_text}\'">')