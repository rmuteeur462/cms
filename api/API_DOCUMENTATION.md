# WSSP CMS API Documentation & Standards (v1)

This handbook defines the official design system, communication standards, and conventions for the WSSP Complaint Management System REST API.

---

## 1. Base URL & Versioning

All version 1 endpoints must be prefixed with:
```http
/api/cms/v1/
```

- Current Production Version: `v1`
- Content Type: `application/json; charset=utf-8` (or `multipart/form-data` for uploads)

---

## 2. Standard Response Format

All API responses must follow a consistent top-level JSON structure.

### 2.1 Success Response

```json
{
    "success": true,
    "data": {
        "id": 1024,
        "title": "Water Pipe Leakage",
        "status": "in_progress"
    },
    "message": "Operation completed successfully"
}
```

### 2.2 Error Response

```json
{
    "success": false,
    "message": "Invalid credentials or unauthorized access"
}
```

### 2.3 Field-Level Validation Error Response

When a form or input serializer validation fails (`HTTP 400 Bad Request`):

```json
{
    "success": false,
    "message": "Validation failed",
    "errors": {
        "complaint_type": ["This field is required."],
        "phone_number": ["Enter a valid 11-digit mobile number."]
    }
}
```

---

## 3. Authentication & Authorization

- **Scheme**: JSON Web Token (JWT)
- **Header**: `Authorization: Bearer <access_token>`
- **Token Expiry**:
  - Access Token: 24 Hours
  - Refresh Token: 7 Days
- **Refresh Flow**: Send refresh token to `/api/cms/auth/refresh/` to obtain a fresh access token without re-entering credentials.

### Zonal & Departmental Security Matrix
Every authenticated request is scoped according to the user's role profile:
1. **Head Office**: Cross-zonal access to all complaints and stats across Zone A, B, C, D, etc.
2. **Zonal Manager**: Filtered strictly to their assigned Zone.
3. **Department Manager / SWM / WS / SDS**: Filtered strictly to their assigned Zone AND assigned Department.

---

## 4. Pagination Standard

Endpoints returning list collections must support pagination to maintain mobile speed and reduce bandwidth consumption.

### Query Parameters
- `page`: Page index (integer, default: `1`)
- `page_size`: Records per page (integer, default: `20`, maximum: `100`)

### Paginated Response Structure
```json
{
    "success": true,
    "data": {
        "count": 1420,
        "next": "http://127.0.0.1:8000/api/cms/v1/complaints/?page=2",
        "previous": null,
        "page": 1,
        "total_pages": 71,
        "results": [
            {
                "id": 1,
                "ticket_no": "WSSP-2026-001"
            }
        ]
    },
    "message": "Records fetched successfully"
}
```

---

## 5. HTTP Status Codes

| Code | Name | Description |
|---|---|---|
| `200 OK` | Success | Standard response for successful GET, PUT, PATCH requests. |
| `201 Created` | Resource Created | Successful POST creating a new resource (e.g., complaint). |
| `204 No Content` | Deleted | Successful DELETE request with empty body. |
| `400 Bad Request` | Validation Failure | Invalid input payload or missing required parameters. |
| `401 Unauthorized` | Not Authenticated | Missing or expired JWT token. |
| `403 Forbidden` | Permission Denied | User authenticated, but lacks zonal/departmental privilege. |
| `404 Not Found` | Missing Resource | The requested complaint, user, or entity does not exist. |
| `500 Internal Error` | Server Error | Unhandled backend exception (logged to server logs). |

---

## 6. API Naming Conventions

- **URIs**: Lowercase nouns in plural form separated by hyphens (kebab-case) or slashes.
  - Good: `/api/cms/v1/complaint-types/`
  - Bad: `/api/cms/v1/getComplaintTypes`
- **JSON Keys**: `snake_case` (e.g., `ticket_no`, `created_at`, `zone_name`, `assigned_to`).
- **Trailing Slash**: All endpoints end with a trailing slash `/` per standard Django conventions.

---

## 7. Date and Time Format

All timestamps are stored and transmitted in **ISO 8601 UTC format**:
```
YYYY-MM-DDTHH:MM:SS.sssZ
Example: "2026-09-14T06:18:00.000Z"
```
The React Native client is responsible for rendering local Pakistan Standard Time (PKT, UTC+5) for display.

---

## 8. File & Media Upload Rules

When submitting complaint photos or response attachments:
- **Encoding**: `multipart/form-data`
- **Supported File Types**:
  - Images: `.jpg`, `.jpeg`, `.png`, `.webp`
  - Documents: `.pdf`
- **File Size Limit**: Max `5 MB` per file.
- **Image Optimization**: Mobile app should compress images before transmission; server performs safety scan and saves to media storage.

---

## 9. Core Endpoints Reference

### Service Status
- **GET** `/api/cms/v1/status/`
  - Public health check confirming API v1 availability.
