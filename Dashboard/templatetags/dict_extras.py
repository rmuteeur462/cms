from django import template

register = template.Library()

@register.filter
def render_form(dictionary, key):
    """Safely render a form from a dict by key."""
    form = dictionary.get(key)
    return form.as_p() if form else ''
