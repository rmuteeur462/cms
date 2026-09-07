from django import template

register = template.Library()

# =========================
# Get dictionary item
# =========================
@register.filter
def get_item(dictionary, key):
    if not dictionary:
        return None
    return dictionary.get(key)


# =========================
# Get object attribute dynamically
# =========================
@register.filter
def get_attr(obj, attr):
    if not obj:
        return None
    return getattr(obj, attr, None)