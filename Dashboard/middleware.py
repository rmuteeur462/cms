from django.utils.timezone import now
from .models import UserActivityLog
import logging

# Set up a logger for debugging
logger = logging.getLogger(__name__)

class UserActivityTrackingMiddleware:
    """
    Middleware that logs user activities for add, update, and delete actions.
    It tracks the HTTP methods and logs them as user activity.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            action = None
            model_name = None
            object_id = None
            description = None

            # Check if the request is a form submission (POST, PUT, DELETE)
            if request.method == 'POST':
                action = 'ADD'
                model_name = request.POST.get('model_name')
                object_id = request.POST.get('object_id')
                description = f"Created {model_name} with ID: {object_id}"
                logger.debug(f"POST data: model_name={model_name}, object_id={object_id}")

            elif request.method == 'PUT':
                action = 'UPDATE'
                model_name = request.POST.get('model_name')
                object_id = request.POST.get('object_id')
                description = f"Updated {model_name} with ID: {object_id}"
                logger.debug(f"PUT data: model_name={model_name}, object_id={object_id}")

            elif request.method == 'DELETE':
                action = 'DELETE'
                model_name = request.POST.get('model_name')
                object_id = request.POST.get('object_id')
                description = f"Deleted {model_name} with ID: {object_id}"
                logger.debug(f"DELETE data: model_name={model_name}, object_id={object_id}")

            # Log the activity if we identified an action and the necessary data
            if action and model_name and object_id:
                try:
                    # Create the activity log entry
                    UserActivityLog.objects.create(
                        user=request.user,
                        action=action,
                        model_name=model_name,
                        object_id=object_id,
                        description=description,
                        timestamp=now()
                    )
                    logger.info(f"Activity log created for {action} {model_name} with ID: {object_id}")
                except Exception as e:
                    # Log any errors that occur during the logging process
                    logger.error(f"Error while logging activity: {e}")

        # Process the response
        response = self.get_response(request)
        return response








from .models import Log  # Changed import to Log

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

class UserActivityLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            Log.objects.create(  # Changed model name to Log
                user=request.user,
                action=f"Accessed {request.path}",
                method=request.method,
                path=request.path,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                status_code=response.status_code,
            )
        return response


from .models import Log  # Changed import to Log

def log_admin_action(request, action, obj=None):
    """
    Log admin actions with additional details.
    """
    Log.objects.create(  # Changed model name to Log
        user=request.user,
        action=action if obj is None else f"{action}: {obj}",
        method=request.method,
        path=request.path,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
    )



