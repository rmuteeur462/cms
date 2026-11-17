"""
API v1 Citizen Serializers
==========================
Defines request and response serializers for citizen registration,
authentication, and profile management.
"""

import re
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

from api.models import CitizenProfile
from Dashboard.models import Complaint, ComplaintFeedback, ComplaintResolution
from api.v1.permissions.base import get_user_allowed_location_ids


def normalize_pakistan_mobile(mobile_raw: str) -> str:
    """
    Normalizes any Pakistani mobile number representation to standard 11-digit '03XXXXXXXXX'.
    Examples:
        '+923001234567' -> '03001234567'
        '923001234567'  -> '03001234567'
        '0300-1234567'  -> '03001234567'
        '0300 1234567'  -> '03001234567'
    """
    if not mobile_raw:
        raise serializers.ValidationError("Mobile number is required.")

    # Remove all spaces, hyphens, parentheses, and plus signs
    cleaned = re.sub(r"[\s\-\(\)\+]", "", str(mobile_raw).strip())

    # Replace leading international codes
    if cleaned.startswith("0092"):
        cleaned = "0" + cleaned[4:]
    elif cleaned.startswith("92"):
        cleaned = "0" + cleaned[2:]

    # Validate final standard Pakistani 11-digit mobile format
    if not re.match(r"^03\d{9}$", cleaned):
        raise serializers.ValidationError(
            "Please enter a valid 11-digit Pakistani mobile number (e.g. 03001234567)."
        )

    return cleaned


class CitizenRegistrationSerializer(serializers.Serializer):
    """
    Serializer for public citizen self-registration.
    Requires full name, mobile number, and password confirmation.
    No OTP / SMS / email verification required.
    """
    full_name = serializers.CharField(
        max_length=150,
        required=True,
        error_messages={"required": "Full name is required."},
    )
    mobile_number = serializers.CharField(
        max_length=20,
        required=True,
        error_messages={"required": "Mobile number is required."},
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={"input_type": "password"},
        error_messages={
            "required": "Password is required.",
            "min_length": "Password must be at least 8 characters long.",
        },
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        error_messages={"required": "Please confirm your password."},
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        default="",
    )
    address = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        max_length=500,
    )

    def validate_full_name(self, value):
        name = value.strip()
        if len(name) < 2:
            raise serializers.ValidationError("Full name must be at least 2 characters long.")
        return name

    def validate_mobile_number(self, value):
        normalized = normalize_pakistan_mobile(value)

        # Check for duplicate user accounts
        if User.objects.filter(username=normalized).exists():
            raise serializers.ValidationError(
                "An account with this mobile number already exists. Please log in instead."
            )

        if CitizenProfile.objects.filter(mobile_number=normalized).exists():
            raise serializers.ValidationError(
                "An account with this mobile number already exists. Please log in instead."
            )

        return normalized

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        # 1. Password confirmation match
        if password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match. Please re-enter."}
            )

        # 2. Check that password is not purely numeric
        if password.isdigit():
            raise serializers.ValidationError(
                {"password": "Password cannot be entirely numeric. Include letters and numbers."}
            )

        # 3. Standard Django password validation checks
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs


class CitizenLoginSerializer(serializers.Serializer):
    """
    Serializer for citizen login using mobile number and password.
    Enforces that staff or unauthorized users cannot authenticate through this endpoint.
    """
    mobile_number = serializers.CharField(
        required=True,
        error_messages={"required": "Mobile number is required."},
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
        error_messages={"required": "Password is required."},
    )

    def validate(self, attrs):
        raw_mobile = attrs.get("mobile_number")
        password = attrs.get("password")

        # Normalize mobile format to match username
        try:
            normalized_mobile = normalize_pakistan_mobile(raw_mobile)
        except serializers.ValidationError:
            raise serializers.ValidationError(
                {"mobile_number": "Invalid mobile number format. Use 11-digit format (e.g. 03001234567)."}
            )

        # Authenticate against Django's auth_user table
        user = authenticate(username=normalized_mobile, password=password)

        if not user:
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid mobile number or password. Please try again."]}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": ["This account has been deactivated. Please contact WSSP helpline 1334."]}
            )

        # Account Separation Security Check:
        # Staff and superusers must use the staff portal, not the citizen portal.
        if user.is_staff or user.is_superuser:
            raise serializers.ValidationError(
                {"non_field_errors": ["Staff members must log in through the WSSP Staff Portal."]}
            )

        allowed_location_ids = get_user_allowed_location_ids(user)
        if len(allowed_location_ids) > 0:
            raise serializers.ValidationError(
                {"non_field_errors": ["Staff members must log in through the WSSP Staff Portal."]}
            )

        attrs["user"] = user
        attrs["normalized_mobile"] = normalized_mobile
        return attrs


class CitizenProfileSerializer(serializers.ModelSerializer):
    """
    Read/update serializer for citizen profile details.
    Allows updating address, full_name, and email.
    """
    full_name = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False, allow_blank=True)
    role = serializers.SerializerMethodField()
    account_type = serializers.SerializerMethodField()

    class Meta:
        model = CitizenProfile
        fields = [
            "id",
            "mobile_number",
            "full_name",
            "email",
            "address",
            "role",
            "account_type",
            "created_at",
        ]
        read_only_fields = ["id", "mobile_number", "created_at"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        full_name = f"{instance.user.first_name} {instance.user.last_name}".strip()
        ret["full_name"] = full_name or instance.user.username
        ret["email"] = instance.user.email
        return ret

    def get_role(self, obj):
        return "Citizen"

    def get_account_type(self, obj):
        return "citizen"

    def update(self, instance, validated_data):
        user = instance.user

        # 1. Update full_name on User
        full_name = validated_data.pop("full_name", None)
        if full_name is not None:
            full_name = full_name.strip()
            parts = full_name.split(" ", 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ""

        # 2. Update email on User
        email = validated_data.pop("email", None)
        if email is not None:
            user.email = email.strip()

        user.save()

        # 3. Update profile fields (address)
        instance.address = validated_data.get("address", instance.address)
        instance.save()

        return instance


class CitizenComplaintCreateSerializer(serializers.Serializer):
    """
    Serializer validating citizen complaint registration requests.
    Supports form-data, JSON, and multipart file uploads.
    """
    complaint_type_id = serializers.IntegerField(
        required=True,
        error_messages={"required": "Please select a complaint category."},
    )
    subtype_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        default=None,
    )
    uc_id = serializers.IntegerField(
        required=True,
        error_messages={"required": "Please select your Union Council."},
    )
    complaint_detail = serializers.CharField(
        required=True,
        min_length=10,
        max_length=2000,
        error_messages={
            "required": "Please provide a detailed description of the complaint.",
            "min_length": "Complaint description must be at least 10 characters long.",
        },
    )
    address = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        max_length=500,
    )
    area = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        max_length=100,
    )
    title = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        max_length=150,
    )
    latitude = serializers.DecimalField(
        required=False,
        allow_null=True,
        default=None,
        max_digits=9,
        decimal_places=6,
    )
    longitude = serializers.DecimalField(
        required=False,
        allow_null=True,
        default=None,
        max_digits=9,
        decimal_places=6,
    )


class CitizenComplaintResponseSerializer(serializers.ModelSerializer):
    """
    Serializes a created or viewed complaint for the citizen.
    Exposes official reference ticket number CMS-{id}.
    """
    complaint_no = serializers.SerializerMethodField()
    category = serializers.CharField(source="complaint_type.type_name", read_only=True)
    subcategory = serializers.CharField(source="SubType.type_name", read_only=True, default=None)
    location_name = serializers.CharField(source="location.location_name", read_only=True)
    uc_name = serializers.CharField(source="uc.uc_name", read_only=True, default=None)
    before_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Complaint
        fields = [
            "id",
            "complaint_no",
            "title",
            "category",
            "subcategory",
            "location_name",
            "uc_name",
            "area",
            "address",
            "complaint_detail",
            "status",
            "date",
            "before_image_url",
            "created_at",
        ]

    def get_complaint_no(self, obj):
        return f"CMS-{obj.id}"

    def get_before_image_url(self, obj):
        if not obj.before_image:
            return None
        request = self.context.get("request")
        if request:
            try:
                return request.build_absolute_uri(obj.before_image.url)
            except Exception:
                pass
        return obj.before_image.url


class CitizenFeedbackSerializer(serializers.ModelSerializer):
    """
    Serializes a feedback entry submitted for a complaint.
    """
    class Meta:
        model = ComplaintFeedback
        fields = [
            "id",
            "happy",
            "complaint_feedback",
            "created_at",
        ]


class CitizenFeedbackCreateSerializer(serializers.Serializer):
    """
    Validates citizen satisfaction feedback submitted after complaint resolution.
    """
    happy = serializers.BooleanField(
        required=True,
        error_messages={"required": "Please indicate whether you are satisfied (Yes/No)."},
    )
    complaint_feedback = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        max_length=1000,
    )


class CitizenResolutionSerializer(serializers.ModelSerializer):
    """
    Serializes resolution information for resolved complaints.
    """
    after_image_url = serializers.SerializerMethodField()

    class Meta:
        model = ComplaintResolution
        fields = [
            "description",
            "customer_satisfaction",
            "after_image_url",
        ]

    def get_after_image_url(self, obj):
        if not obj.after_image:
            return None
        request = self.context.get("request")
        if request:
            try:
                return request.build_absolute_uri(obj.after_image.url)
            except Exception:
                pass
        return obj.after_image.url


class CitizenComplaintListItemSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for citizen's 'My Complaints' list screen.
    Includes status badges, category names, reference number, and feedback status.
    """
    complaint_no = serializers.SerializerMethodField()
    category = serializers.CharField(source="complaint_type.type_name", read_only=True)
    subcategory = serializers.CharField(source="SubType.type_name", read_only=True, default=None)
    location_name = serializers.CharField(source="location.location_name", read_only=True)
    uc_name = serializers.CharField(source="uc.uc_name", read_only=True, default=None)
    before_image_url = serializers.SerializerMethodField()
    has_feedback = serializers.SerializerMethodField()

    class Meta:
        model = Complaint
        fields = [
            "id",
            "complaint_no",
            "title",
            "category",
            "subcategory",
            "location_name",
            "uc_name",
            "area",
            "address",
            "complaint_detail",
            "status",
            "date",
            "before_image_url",
            "created_at",
            "has_feedback",
        ]

    def get_complaint_no(self, obj):
        return f"CMS-{obj.id}"

    def get_before_image_url(self, obj):
        if not obj.before_image:
            return None
        request = self.context.get("request")
        if request:
            try:
                return request.build_absolute_uri(obj.before_image.url)
            except Exception:
                pass
        return obj.before_image.url

    def get_has_feedback(self, obj):
        return obj.feedbacks.exists()


class CitizenComplaintDetailSerializer(serializers.ModelSerializer):
    """
    Comprehensive public detail serializer for a single citizen complaint.
    Includes resolution info and submitted feedbacks while strictly omitting
    internal staff remarks and internal routing notes.
    """
    complaint_no = serializers.SerializerMethodField()
    category = serializers.CharField(source="complaint_type.type_name", read_only=True)
    subcategory = serializers.CharField(source="SubType.type_name", read_only=True, default=None)
    location_name = serializers.CharField(source="location.location_name", read_only=True)
    uc_name = serializers.CharField(source="uc.uc_name", read_only=True, default=None)
    before_image_url = serializers.SerializerMethodField()
    resolution = serializers.SerializerMethodField()
    feedbacks = CitizenFeedbackSerializer(many=True, read_only=True)
    can_give_feedback = serializers.SerializerMethodField()

    class Meta:
        model = Complaint
        fields = [
            "id",
            "complaint_no",
            "title",
            "category",
            "subcategory",
            "location_name",
            "uc_name",
            "area",
            "address",
            "complaint_detail",
            "status",
            "date",
            "before_image_url",
            "created_at",
            "updated_at",
            "resolution",
            "feedbacks",
            "can_give_feedback",
        ]

    def get_complaint_no(self, obj):
        return f"CMS-{obj.id}"

    def get_before_image_url(self, obj):
        if not obj.before_image:
            return None
        request = self.context.get("request")
        if request:
            try:
                return request.build_absolute_uri(obj.before_image.url)
            except Exception:
                pass
        return obj.before_image.url

    def get_resolution(self, obj):
        if hasattr(obj, "resolution") and obj.resolution:
            return CitizenResolutionSerializer(obj.resolution, context=self.context).data
        return None

    def get_can_give_feedback(self, obj):
        # Feedback is allowed if the complaint is resolved
        return obj.status == "resolved"


