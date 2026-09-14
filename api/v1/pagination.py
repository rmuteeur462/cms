"""
API v1 Standard Pagination
==========================
Defines consistent pagination styles for list endpoints.
Ensures mobile clients receive deterministic page chunks (default: 20)
and protects server memory against loading tens of thousands of records.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination for mobile collections (e.g. complaints list).
    - default page_size: 20
    - client override: ?page_size=X (up to 100)
    - client page: ?page=Y
    """
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "success": True,
            "data": {
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            },
            "message": "Records retrieved successfully."
        })
