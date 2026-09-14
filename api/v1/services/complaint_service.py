"""
API v1 Complaint Service Layer
==============================
Handles transactional business operations and state transitions for complaints:
- History aggregation (Actions, Responses, Feedbacks, Resolution)
- Adding officer responses
- Resolving complaints with resolution records and after-image attachments
- Complaint partial updates with automatic audit logging
"""

from django.db import transaction
from Dashboard.models import (
    Complaint,
    ComplaintResolution,
    ComplaintResponse,
    ComplaintActionLog,
    ComplaintFeedback,
)


class ComplaintService:
    """
    Central business logic coordinator for Complaint workflows.
    Guarantees consistent audit trails and model integrity.
    """

    @staticmethod
    def get_complaint_history(complaint, request=None):
        """
        Gathers complete chronological timeline for a complaint:
        - Audit logs (ComplaintActionLog)
        - Officer responses (ComplaintResponse)
        - Citizen feedback (ComplaintFeedback)
        - Resolution details (ComplaintResolution)
        """
        # 1. Action Logs
        actions = []
        for action in complaint.actions.select_related("user").order_by("-timestamp"):
            user_name = action.user.username if action.user else "System"
            actions.append({
                "id": action.id,
                "action": action.action,
                "user": user_name,
                "timestamp": action.timestamp,
            })

        # 2. Officer Responses
        responses = []
        for resp in complaint.responses.all().order_by("-created_at"):
            responses.append({
                "id": resp.id,
                "officer_name": resp.officer_name,
                "feedback": resp.feedback,
                "created_at": resp.created_at,
            })

        # 3. Citizen Feedback
        feedbacks = []
        for fb in complaint.feedbacks.all().order_by("-created_at"):
            feedbacks.append({
                "id": fb.id,
                "officer_name": fb.feedback_officer_name,
                "feedback_text": fb.complaint_feedback,
                "happy": fb.happy,
                "created_at": fb.created_at,
            })

        # 4. Resolution
        resolution_data = None
        if hasattr(complaint, "resolution") and complaint.resolution:
            res = complaint.resolution
            after_image_url = None
            if res.after_image:
                try:
                    if request:
                        after_image_url = request.build_absolute_uri(res.after_image.url)
                    else:
                        after_image_url = res.after_image.url
                except Exception:
                    after_image_url = None

            resolution_data = {
                "id": res.id,
                "description": res.description,
                "customer_satisfaction": res.customer_satisfaction,
                "after_image_url": after_image_url,
            }

        return {
            "complaint_id": complaint.id,
            "status": complaint.status,
            "actions": actions,
            "responses": responses,
            "feedbacks": feedbacks,
            "resolution": resolution_data,
        }

    @staticmethod
    @transaction.atomic
    def add_response(complaint, user, feedback, officer_name=None):
        """
        Records an official response to a complaint.
        """
        if not officer_name:
            full_name = f"{user.first_name} {user.last_name}".strip()
            officer_name = full_name if full_name else user.username

        response_obj = ComplaintResponse.objects.create(
            complaint=complaint,
            officer_name=officer_name,
            feedback=feedback,
        )

        # Log the action (using 'created' or custom action representation)
        ComplaintActionLog.objects.create(
            complaint=complaint,
            user=user,
            action="responded",
        )

        return response_obj

    @staticmethod
    @transaction.atomic
    def resolve_complaint(complaint, user, description=None, customer_satisfaction="yes", after_image=None):
        """
        Transitions complaint status to 'resolved' and creates/updates ComplaintResolution.
        """
        # 1. Update Complaint status
        complaint.status = "resolved"
        complaint.save(update_fields=["status", "updated_at"])

        # 2. Create or update ComplaintResolution
        resolution_obj, _ = ComplaintResolution.objects.get_or_create(
            complaint=complaint,
            defaults={
                "description": description,
                "customer_satisfaction": customer_satisfaction,
                "after_image": after_image,
            },
        )
        if not _:
            if description is not None:
                resolution_obj.description = description
            if customer_satisfaction is not None:
                resolution_obj.customer_satisfaction = customer_satisfaction
            if after_image is not None:
                resolution_obj.after_image = after_image
            resolution_obj.save()

        # 3. Log the resolution action
        ComplaintActionLog.objects.create(
            complaint=complaint,
            user=user,
            action="resolved",
        )

        return resolution_obj

    @staticmethod
    @transaction.atomic
    def update_complaint(complaint, user, validated_data):
        """
        Partially updates allowed fields on a complaint and creates an action log.
        """
        for field, value in validated_data.items():
            setattr(complaint, field, value)

        complaint.save()

        ComplaintActionLog.objects.create(
            complaint=complaint,
            user=user,
            action="updated",
        )

        return complaint
