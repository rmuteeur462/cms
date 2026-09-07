# your_app/templatetags/tubewell_filters.py
from django import template

register = template.Library()

@register.filter
def get_count(d, key):
    """Return the value for a key from a dictionary, default 0"""
    return d.get(key, 0)
