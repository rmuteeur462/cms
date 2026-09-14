"""
API v1 Reference Data Serializers
=================================
Serializers for static lookup and dropdown metadata required by complaint forms:
- Complaint Types (Solid Waste, Water Supply, Drainage, Billing)
- Complaint Sub-Types (hierarchically linked to complaint types)
- Locations (Zones & Headoffice)
- Union Councils (UCs, linked to Locations)
- Complaint Sources (Walk-In, Phone, App, Social Media)
"""

from rest_framework import serializers
from Dashboard.models import ComplaintType, ComplaintSubType, Location, UC, ComplaintSource


class ComplaintTypeSerializer(serializers.ModelSerializer):
    """Serializes ComplaintType for form selection."""
    class Meta:
        model = ComplaintType
        fields = ["id", "type_name"]


class ComplaintSubTypeSerializer(serializers.ModelSerializer):
    """Serializes ComplaintSubType with parent complaint type metadata."""
    complaint_type_name = serializers.CharField(source="complaint_type.type_name", read_only=True, default=None)

    class Meta:
        model = ComplaintSubType
        fields = ["id", "type_name", "complaint_type", "complaint_type_name"]


class LocationSerializer(serializers.ModelSerializer):
    """Serializes Location (Zones / Headoffice)."""
    class Meta:
        model = Location
        fields = ["id", "location_name"]


class UCSerializer(serializers.ModelSerializer):
    """Serializes Union Council (UC) records with zonal relationship."""
    location_name = serializers.CharField(source="location.location_name", read_only=True, default=None)

    class Meta:
        model = UC
        fields = ["id", "uc_name", "location", "location_name"]


class ComplaintSourceSerializer(serializers.ModelSerializer):
    """Serializes complaint intake channels."""
    class Meta:
        model = ComplaintSource
        fields = ["id", "source_name"]
