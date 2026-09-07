from django.shortcuts import render
from .models import UserViewPermission, ViewName

def view_permission_required(view_name):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            # Allow superusers to access all views without permission checks
            if request.user.is_superuser:
                return func(request, *args, **kwargs)

            # Check if the user has permission for the specified view
            if not UserViewPermission.objects.filter(
                user=request.user,
                view_name__name=view_name,
                can_view=True
            ).exists():
                # Prepare the message using the user's username
                message = f"Sorry {request.user.username}, you do not have permission to view this page."
                # Render a template with the modal
                return render(request, 'forbidden.html', {'message': message})

            return func(request, *args, **kwargs)
        return wrapper
    return decorator
