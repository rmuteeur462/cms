# Dashboard/utils.py

from .models import Log  # Ensure Log is imported


# Dashboard/utils.py

def get_client_ip(request):
    """
    Extract the client's IP address from the request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_admin_action(request, action, obj=None):
    """
    Log admin actions with additional details.
    """
    Log.objects.create(  # Use Log instead of UserActivityLog
        user=request.user,
        action=action if obj is None else f"{action}: {obj}",
        method=request.method,
        path=request.path,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
    )
