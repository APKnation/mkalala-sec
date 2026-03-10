from django import template

register = template.Library()

@register.filter
def add_class(value, css_class):
    """
    Adds CSS class to form field widget
    """
    if hasattr(value, 'field'):
        # It's a BoundField
        if value.field.widget.attrs.get('class'):
            value.field.widget.attrs['class'] += ' ' + css_class
        else:
            value.field.widget.attrs['class'] = css_class
    return value
