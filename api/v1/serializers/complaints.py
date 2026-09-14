"""
API v1 Complaint Serializers
============================
Transforms Complaint ORM instances into mobile-optimized JSON responses.
Matches real WSSP model fields:
- complaint_no / id
- title, status, date
- complaint_type (id, name)
- SubType (id, name)
- location (id, name)
- uc (id, name)
- address, complaint_detail
- citizen metadata & channel info
"""

from rest_framework import serializers
from Dashboard.models import Complaint


class ComplaintListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for complaint listing & infinite scroll.
    Omits heavy binary/large payloads for optimal mobile performance.
    """
    complaint_no = serializers.SerializerMethodField()
    complaint_type = serializers.SerializerMethodField()
    subtype = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    uc = serializers.SerializerMethodField()

    class Meta:
        model = Complaint
        fields = [
            "id",
            "complaint_no",
            "title",
            "status",
            "date",
            "complaint_type",
            "subtype",
            "location",
            "uc",
            "address",
            "area",
            "complaint_detail",
            "created_at",
        ]

    def get_complaint_no(self, obj):
        return f"CMS-{obj.id}"

    def get_complaint_type(self, obj):
        if obj.complaint_type:
            return {"id": obj.complaint_type.id, "name": obj.complaint_type.type_name}
        return None

    def get_subtype(self, obj):
        if obj.SubType:
            return {"id": obj.SubType.id, "name": obj.SubType.type_name}
        return None

    def get_location(self, obj):
        if obj.location:
            return {"id": obj.location.id, "name": obj.location.location_name}
        return None

    def get_uc(self, obj):
        if obj.uc:
            return {"id": obj.uc.id, "name": obj.uc.uc_name}
        return None


class ComplaintDetailSerializer(ComplaintListSerializer):
    """
    Comprehensive serializer for complaint detail view.
    Includes citizen data, complaint channels, and before image attachment.
    """
    complaint_source = serializers.SerializerMethodField()
    before_image_url = serializers.SerializerMethodField()

    class Meta(ComplaintListSerializer.Meta):
        fields = ComplaintListSerializer.Meta.fields + [
            "first_name",
            "last_name",
            "cell_number",
            "phone_number",
            "cnic",
            "consumer_type",
            "gender",
            "tehsil",
            "bill_number",
            "type",
            "complaint_source",
            "Pcp_compalin_no",
            "Eak_compalin_no",
            "Ebaldia_compalin_no",
            "before_image_url",
            "updated_at",
        ]

    def get_complaint_source(self, obj):
        if obj.complaint_source:
            return {"id": obj.complaint_source.id, "name": obj.complaint_source.source_name}
        return None

    def get_before_image_url(self, obj):
        if obj.before_image:
            try:
                request = self.context.get("request")
                if request:
                    return request.build_absolute_uri(obj.before_image.url)
                return obj.before_image.url
            except Exception:
                return None
        return None
