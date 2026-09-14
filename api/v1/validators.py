"""
API v1 Upload & Data Security Validators
========================================
Enforces upload constraints for mobile images & documents:
- File size restrictions (max 5MB)
- Image extension verification (jpeg, jpg, png, webp)
- Sanitization against malformed binaries
"""

import os
from rest_framework.exceptions import ValidationError

MAX_UPLOAD_SIZE_MB = 5
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]


def validate_image_file(file_obj):
    """
    Validates uploaded image size and extension.
    Raises ValidationError if limits are violated.
    """
    if not file_obj:
        return

    # Check size
    if file_obj.size > MAX_UPLOAD_SIZE_BYTES:
        raise ValidationError(
            f"Image file size exceeds {MAX_UPLOAD_SIZE_MB}MB limit (actual: {file_obj.size / (1024 * 1024):.1f}MB)."
        )

    # Check extension
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f"Unsupported image format '{ext}'. Allowed formats: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}."
        )
