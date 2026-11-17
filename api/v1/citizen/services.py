"""
API v1 Citizen Services Layer
=============================
Encapsulates business operations for public citizen complaints:
- Submission validation and taxonomy consistency
- Automatic zone resolution from verified location hierarchy
- Duplicate submission prevention
- Audit trail initialization
- Departmental routing verification
"""

from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework import serializers

from Dashboard.models import (
    Complaint,
    ComplaintType,
    ComplaintSubType,
    ComplaintSource,
    UC,
    Location,
    ComplaintActionLog,
)
from api.models import CitizenProfile

# Maximum image upload size: 5 MB
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "heic"}


class CitizenComplaintSubmissionService:
    """
    Coordinates atomic validation, zone resolution, and persistence
    for citizen-submitted complaints.
    """

    @classmethod
    def validate_image_file(cls, image_file):
        """Validates uploaded image file size and extension."""
        if not image_file:
            return

        if image_file.size > MAX_IMAGE_SIZE_BYTES:
            raise serializers.ValidationError(
                {"before_image": "Photograph size exceeds 5MB limit. Please upload a smaller image."}
            )

        filename = getattr(image_file, "name", "").lower()
        ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise serializers.ValidationError(
                {"before_image": f"Invalid image format (.{ext}). Supported formats: JPG, PNG, WEBP."}
            )

    @classmethod
    def check_duplicate_submission(cls, citizen_user, uc, complaint_type, complaint_detail):
        """
        Prevents accidental double-taps and rapid re-submissions
        from the same citizen within a 60-second window.
        """
        one_minute_ago = timezone.now() - timedelta(seconds=60)
        recent_duplicate = Complaint.objects.filter(
            cell_number=citizen_user.username,
            uc=uc,
            complaint_type=complaint_type,
            complaint_detail=complaint_detail,
            created_at__gte=one_minute_ago,
        ).exists()

        if recent_duplicate:
            raise serializers.ValidationError(
                {"detail": "A complaint with identical details was just submitted. Please wait a minute before submitting again."}
            )

    @classmethod
    @transaction.atomic
    def submit_complaint(cls, citizen_user, validated_data, image_file=None):
        """
        Atomically creates a citizen complaint:
        1. Resolves verified Location (Zone) from Union Council (uc.location).
        2. Validates that subtype belongs to the specified complaint type.
        3. Populates applicant fields from citizen profile.
        4. Saves Complaint record with 'pending' status.
        5. Logs creation audit action in ComplaintActionLog.
        """
        complaint_type_id = validated_data["complaint_type_id"]
        subtype_id = validated_data.get("subtype_id")
        uc_id = validated_data["uc_id"]
        complaint_detail = validated_data["complaint_detail"].strip()
        address = validated_data.get("address", "").strip()
        area = validated_data.get("area", "").strip()
        title = validated_data.get("title", "").strip()
        latitude = validated_data.get("latitude")
        longitude = validated_data.get("longitude")

        # 1. Resolve Complaint Type
        try:
            complaint_type = ComplaintType.objects.get(id=complaint_type_id)
        except ComplaintType.DoesNotExist:
            raise serializers.ValidationError({"complaint_type_id": "Selected complaint category does not exist."})

        # 2. Resolve and Validate Subtype
        subtype = None
        if subtype_id:
            try:
                subtype = ComplaintSubType.objects.get(id=subtype_id)
                if subtype.complaint_type_id != complaint_type.id:
                    raise serializers.ValidationError(
                        {"subtype_id": f"Subcategory '{subtype.type_name}' does not belong to '{complaint_type.type_name}'."}
                    )
            except ComplaintSubType.DoesNotExist:
                raise serializers.ValidationError({"subtype_id": "Selected subcategory does not exist."})

        # 3. Resolve Union Council & Verified Zone
        try:
            uc = UC.objects.select_related("location").get(id=uc_id)
        except UC.DoesNotExist:
            raise serializers.ValidationError({"uc_id": "Selected Union Council (UC) does not exist."})

        # CRITICAL SECURITY RULE: Verified Zone is resolved directly from UC hierarchy
        # Do not trust a client-supplied zone
        location = uc.location
        if not location:
            raise serializers.ValidationError({"uc_id": "Union Council is not mapped to an operational WSSP Zone."})

        # 4. Check Duplicate Submissions
        cls.check_duplicate_submission(citizen_user, uc, complaint_type, complaint_detail)

        # 5. Validate Image (if uploaded)
        if image_file:
            cls.validate_image_file(image_file)

        # 6. Resolve Complaint Source (Mobile App)
        complaint_source = (
            ComplaintSource.objects.filter(source_name__icontains="mobile").first()
            or ComplaintSource.objects.filter(source_name__icontains="app").first()
            or ComplaintSource.objects.first()
        )

        # 7. Extract Citizen Applicant Metadata
        profile = getattr(citizen_user, "citizen_profile", None)
        full_name = f"{citizen_user.first_name} {citizen_user.last_name}".strip() or citizen_user.username
        first_name = citizen_user.first_name or full_name
        last_name = citizen_user.last_name or ""
        cell_number = profile.mobile_number if profile else citizen_user.username

        # If area was not specified, default to UC name
        if not area:
            area = uc.uc_name

        # If address was not specified, fallback to profile address
        if not address and profile and profile.address:
            address = profile.address

        # Append GPS coordinates to address if provided
        if latitude and longitude:
            gps_marker = f"[GPS: {latitude}, {longitude}]"
            if gps_marker not in address:
                address = f"{address}\n{gps_marker}".strip() if address else gps_marker

        # Default title if not provided
        if not title:
            title = subtype.type_name if subtype else complaint_type.type_name

        # 8. Create Complaint Instance
        complaint = Complaint(
            location=location,
            uc=uc,
            complaint_source=complaint_source,
            complaint_type=complaint_type,
            SubType=subtype,
            first_name=first_name,
            last_name=last_name,
            cell_number=cell_number,
            phone_number=None,
            gender="male",  # standard default
            consumer_type="domestic",
            area=area,
            address=address,
            title=title,
            complaint_detail=complaint_detail,
            date=timezone.now().date(),
            status="pending",
        )

        if image_file:
            complaint.before_image = image_file

        complaint.save()

        # 9. Update the post_save signal created log or create Audit Action Log
        action_log = ComplaintActionLog.objects.filter(
            complaint=complaint,
            action="created",
            user__isnull=True,
        ).first()
        if action_log:
            action_log.user = citizen_user
            action_log.save(update_fields=["user"])
        else:
            ComplaintActionLog.objects.create(
                complaint=complaint,
                user=citizen_user,
                action="created",
            )

        return complaint

