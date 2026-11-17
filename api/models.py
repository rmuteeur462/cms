"""
API Models — WSSP Citizen Portal
================================
Defines database models for public citizen profiles and related metadata.
"""

from django.db import models
from django.contrib.auth.models import User


class CitizenProfile(models.Model):
    """
    Profile extension for public citizens.
    Links 1-to-1 with Django's standard User model (where username = mobile_number).
    Stores citizen-specific fields without altering core auth_user table.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="citizen_profile",
        verbose_name="User Account",
    )
    mobile_number = models.CharField(
        max_length=15,
        unique=True,
        db_index=True,
        verbose_name="Mobile Number",
        help_text="Primary 11-digit mobile contact (e.g., 03001234567)",
    )
    address = models.TextField(
        blank=True,
        default="",
        verbose_name="Residential Address",
        help_text="Citizen's street or locality in Peshawar",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Registered At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Citizen Profile"
        verbose_name_plural = "Citizen Profiles"
        ordering = ["-created_at"]

    def __str__(self):
        full_name = f"{self.user.first_name} {self.user.last_name}".strip()
        return f"{full_name or self.user.username} ({self.mobile_number})"
