# custom_filters.py
from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key, 0)

@register.filter(name='dict_get')
def dict_get(dictionary, key):
    """Safely gets a value from a dictionary."""
    return dictionary.get(key, {})

