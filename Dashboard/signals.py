# Dashboard/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import UserActivityLog
from django.contrib.auth.models import User

@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    # Ignore logging for the log model itself
    if sender == UserActivityLog:
        return

    action = 'ADD' if created else 'UPDATE'
    user = getattr(instance, 'updated_by', None) or getattr(instance, 'created_by', None)
    if user and isinstance(user, User):
        UserActivityLog.objects.create(
            user=user,
            action=action,
            model_name=sender.__name__,
            object_id=instance.pk,
            description=f"{action} {sender.__name__} (ID: {instance.pk})",
        )

@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    # Ignore logging for the log model itself
    if sender == UserActivityLog:
        return

    user = getattr(instance, 'deleted_by', None) or getattr(instance, 'updated_by', None)
    if user and isinstance(user, User):
        UserActivityLog.objects.create(
            user=user,
            action='DELETE',
            model_name=sender.__name__,
            object_id=instance.pk,
            description=f"Deleted {sender.__name__} (ID: {instance.pk})",
        )
