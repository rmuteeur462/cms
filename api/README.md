# WSSP CMS API Architecture

Welcome to the WSSP Complaint Management System (CMS) API backend documentation.

## Architecture Overview

The API is engineered using a layered, enterprise-grade architecture:

```
api/
│
├── __init__.py
├── urls.py                      # Main API router (legacy & v1 routing)
│
├── v1/                          # Version 1 Namespace (/api/cms/v1/)
│   ├── __init__.py
│   ├── urls.py                  # v1 endpoint routing
│   ├── views/                   # HTTP handling layer (thin controllers)
│   ├── serializers/             # Schema validation and JSON transformation
│   ├── permissions/             # Multi-tier role & zone access security
│   ├── services/                # Business logic & workflow execution
│   ├── filters/                 # Query parameters & data search
│   └── pagination.py            # Dataset slicing & limits for mobile
│
├── README.md                    # Architecture handbook (this file)
└── API_DOCUMENTATION.md         # API contract & developer specifications
```

---

## Layer Responsibilities

### 1. `views/`
- **Core Question**: *"What should happen when an HTTP request arrives?"*
- **Role**: Validates request method, checks authentication, delegates processing to serializers and services, and formats HTTP responses.
- **Rule**: Keep views thin (< 50-80 lines). Do NOT place heavy business queries directly in views.

### 2. `serializers/`
- **Core Question**: *"What data enters or leaves the system?"*
- **Role**: Validates payload structure, sanitizes input types, transforms Django ORM models into clean JSON schemas for React Native.

### 3. `permissions/`
- **Core Question**: *"Is this specific user allowed to perform this action?"*
- **Role**: Enforces server-side security.
  - **Head Office**: Full cross-zonal access.
  - **Zonal Manager**: Restricted strictly to their assigned Zone (e.g. Zone A).
  - **Department Manager**: Restricted to Zone + Department (e.g. Solid Waste, Water Supply, Sewerage).

### 4. `services/`
- **Core Question**: *"What is the actual business workflow?"*
- **Role**: Handles core system operations:
  - Complaint assignment and reassignment
  - Status lifecycle transitions and validation
  - Audit logging and action history
  - Automated zonal routing logic

### 5. `filters/`
- **Core Question**: *"How do we search and narrow results safely?"*
- **Role**: Safely parses query parameters (status, date range, priority, ward, category) and applies indexed database filters.

### 6. `pagination.py`
- **Core Question**: *"How do we keep responses fast and lightweight?"*
- **Role**: Slices records into pages (default 20 records per page), preventing mobile memory overflow.

---

## Base URLs
- **v1 API Base**: `/api/cms/v1/`
- **Legacy Compatibility**: `/api/cms/`
