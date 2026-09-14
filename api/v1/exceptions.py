"""
API v1 Standard Exception Handler
=================================
Intercepts REST Framework and unhandled server exceptions to format them
into the unified API response contract:
    {
        "success": false,
        "message": "<Error summary>",
        "errors": { ... } (if validation error)
    }
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger("wssp.api")


def custom_api_exception_handler(exc, context):
    """
    Formats all exceptions according to the official API specification.
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_payload = {
            "success": False,
            "message": "An error occurred while processing your request.",
        }

        # Extract message from detail or data
        if isinstance(response.data, dict):
            if "detail" in response.data:
                error_payload["message"] = str(response.data["detail"])
            else:
                error_payload["message"] = "Validation failed."
                error_payload["errors"] = response.data
        elif isinstance(response.data, list):
            error_payload["message"] = " ".join([str(item) for item in response.data])

        response.data = error_payload
    else:
        # Unhandled 500 server exception
        view = context.get("view")
        logger.exception(f"Unhandled API Exception in {view}: {exc}")
        response = Response(
            {
                "success": False,
                "message": "Internal server error. Please contact WSSP technical support.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
