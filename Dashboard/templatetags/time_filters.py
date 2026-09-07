from django import template

register = template.Library()

@register.filter
def hrs_to_dhm(value):
    """
    Convert hours (float) into days, hours, minutes format.
    Example: 96.56 -> "4d 0h 34m"
    """
    try:
        hours = float(value)
    except (ValueError, TypeError):
        return "N/A"

    days = int(hours // 24)
    remaining_hours = int(hours % 24)
    minutes = int(round((hours - int(hours)) * 60))

    return f"{days}d {remaining_hours}h {minutes}m"
