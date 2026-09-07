import base64
from django.conf import settings
from django.http import JsonResponse

def fintech_auth_required(view_func):
    def wrapper(request, *args, **kwargs):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        api_key = request.META.get("HTTP_X_API_KEY")

        if not auth_header or not api_key:
            return JsonResponse({"detail": "Unauthorized"}, status=401)

        if not auth_header.startswith("Basic "):
            return JsonResponse({"detail": "Invalid Authorization"}, status=401)

        try:
            encoded = auth_header.split(" ")[1]
            decoded = base64.b64decode(encoded).decode("utf-8")
            username, password = decoded.split(":")
        except Exception:
            return JsonResponse({"detail": "Invalid Credentials"}, status=401)

        if (
            username != settings.FINTECH_API_USERNAME or
            password != settings.FINTECH_API_PASSWORD or
            api_key != settings.FINTECH_API_KEY
        ):
            return JsonResponse({"detail": "Unauthorized"}, status=401)

        return view_func(request, *args, **kwargs)
    return wrapper
