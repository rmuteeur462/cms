"""
API v1 Services Package
=======================
Encapsulates domain business logic & workflow transactions:
- complaint_service: History extraction, response addition, resolution workflow
"""

from .complaint_service import ComplaintService

__all__ = ["ComplaintService"]
