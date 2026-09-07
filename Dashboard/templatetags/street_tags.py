from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    """Safely get value from dictionary by key"""
    if d and key in d:
        return d[key]
    return None
