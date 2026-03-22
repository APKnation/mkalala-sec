from django import template
from django.templatetags.static import static

register = template.Library()

@register.filter
def image_with_fallback(image_path, alt_text="", fallback_class=""):
    """Return image src with fallback class"""
    if not alt_text:
        alt_text = ""
    if not fallback_class:
        fallback_class = ""
    return f'src="/static/{image_path}" alt="{alt_text}" class="{fallback_class}"'
