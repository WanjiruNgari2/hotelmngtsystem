# The Kitchen Project - Backend (Django)

The Kitchen Project is a role-based restaurant and hotel management system built using Django. It supports various user types (onsite and online customers, waiters, delivery personnel, receptionists, managers, and admins). Support for cleaners and cooks will be added in future iterations. The backend provides structured logic for meals, orders, tipping, feedback, shift management, analytics, and administrative tools.

## Overview

This is the backend layer of the system. It exposes core business logic and RESTful API endpoints that will later be connected to a frontend UI (currently being built using WordPress). It follows Django's philosophy of rapid development, reusable components, clean architecture, and strong admin support.

---

## Table of Contents

* [Requirements and Prerequisites](#requirements-and-prerequisites)
* [Installation Instructions](#installation-instructions)
* [Project Structure](#project-structure)
* [Detailed File Breakdown](#detailed-file-breakdown)
* [API Documentation](#api-documentation)
* [Error Handling](#error-handling)
* [Design Philosophy](#design-philosophy)
* [Future Enhancements](#future-enhancements)
* [Testing](#testing)
* [Troubleshooting](#troubleshooting)
* [Final Notes](#final-notes)

---

## Requirements and Prerequisites

* Python 3.10 or higher
* Django 4.x
* Pillow (for image uploads)
* pipenv or venv for virtual environments
* Git

You must also ensure:

* `pip` is updated (`pip install --upgrade pip`)
* Your virtual environment is activated before running any commands
* Django and Pillow are listed in `requirements.txt`

---

## Installation Instructions

1. Clone the repository:

```bash
git clone https://github.com/yourusername/kitchen-backend.git
cd kitchen-backend
```

2. Set up virtual environment:

```bash
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run database migrations:

```bash
python manage.py migrate
```

5. Create a superuser for admin access:

```bash
python manage.py createsuperuser
```

6. Start the development server:

```bash
python manage.py runserver
```

Admin interface: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## Project Structure

```
hotel/
├── core/                # Core logic (models, views, serializers, admin, urls)
├── hotel/               # Django project settings and URL config
├── manage.py
```

---

## Detailed File Breakdown

### models.py

Defines the core data structure:

* `User`: Custom user model with `email`, `name`, `role`, and `is_staff`. Role values define access (e.g. waiter, delivery, manager).
* `Meal`: Menu item with fields like `name`, `description`, `price`, `image`, and `availability`.
* `Order`: Tracks each customer's order, including its status, timestamps, and related meals/staff.
* `Feedback`: Captures `rating`, `review`, optional `tip`, and links to the service provider.
* `ClockInRecord`: Logs clock-in and clock-out times for users.

### serializers.py

Serializers convert model data to/from JSON:

* `UserSerializer`: Includes essential public fields.
* `MealSerializer`: Serializes all meal details, including images.
* `OrderSerializer`: Nested representation of orders and meals.
* `FeedbackSerializer`: Captures review content, tips, and target user role.

### views.py

Implements business logic via Django REST Framework:

* `admin_stats`: Aggregates platform totals like users, meals, tips, and orders.
* `role_based_reports`: Produces analytics filtered by user role (e.g., delivery personnel).
* Validates query strings, roles, and existence of related records.

Edge Case Handling:

* Invalid query parameters (e.g., missing `role`)
* Invalid roles (not among allowed types)
* Valid but empty queries (returning structured empty lists)
* Null tips or missing feedback entries

### urls.py

Maps endpoints to views:

```python
path('api/admin/stats/', views.admin_stats, name='admin_stats')
path('api/admin/reports/', views.role_based_reports, name='role_reports')
```

Additional CRUD paths for meals, feedback, orders, and users can be added.

---

## API Documentation

### GET `/api/admin/stats/`

Returns high-level metrics across the platform.

**Parameters:** None

**Response:**

```json
{
  "total_users": 120,
  "total_meals": 48,
  "total_orders": 230,
  "total_tips": 15700,
  "total_feedback": 86
}
```

**Error Responses:**

* **500 Internal Server Error**: If database connection fails or an unhandled bug occurs.

---

### GET `/api/admin/reports/?role=delivery`

Returns data for users under a specific role.

**Required Query Parameter:**

* `role`: one of `[waiter, delivery, receptionist, manager]` (cleaners, cooks = todo)

**Response:**

```json
{
  "role": "delivery",
  "personnel": [
    {
      "name": "John Doe",
      "orders_handled": 42,
      "total_tips": 1600,
      "average_rating": 4.5
    }
  ]
}
```

**Error Responses:**

* **400 Bad Request**

  ```json
  {"detail": "Role parameter is required."}
  ```
* **400 Bad Request**

  ```json
  {"detail": "Invalid role provided."}
  ```
* **200 OK** with empty personnel list if no matching records exist

---

## Error Handling

All API endpoints use DRF's built-in and custom exception handling.

| Status Code | Message                                            | Condition Triggering It                    |
| ----------- | -------------------------------------------------- | ------------------------------------------ |
| 400         | Role parameter is required.                        | Query param `role` missing                 |
| 400         | Invalid role provided.                             | Role not in accepted list                  |
| 403         | You do not have permission to perform this action. | User lacks necessary role                  |
| 404         | Not found.                                         | Object queried by ID does not exist        |
| 500         | Internal server error.                             | Unexpected exception (e.g., DB crash, bug) |

---

## Design Philosophy

* Models mirror real-world business logic
* Role-based architecture improves security and clarity
* Views provide clean, scoped access to data
* API-ready structure for frontend or external consumers

---

## Future Enhancements

* Add JWT authentication
* Add cook and cleaner role reporting
* Add order/feedback CRUD APIs
* Add filtering, pagination, and search support
* Add payment gateways (M-Pesa, PayPal)
* Add real-time order notifications via Channels

---

## Testing

Tested manually via Django Admin and Postman.

Scenarios tested:

* Admin stats returns totals correctly
* Reports return correct data or structured empty responses
* Invalid inputs yield proper error messages
* Feedback and tipping logic behave as expected

---

## Troubleshooting

* Ensure your virtual environment is activated before installing or running
* If migrations fail, delete the `db.sqlite3` and `migrations/` folders and try again
* Use `python manage.py runserver` on port 8000 or specify a different port if needed
* Confirm you have the correct role permissions when testing endpoints

---

## Final Notes

This backend is complete for its MVP goals. It is extendable, secure, and production-ready. Frontend integration and more roles are in progress. Use Git to track changes and keep documentation aligned as features expand.

---

## Swagger/OpenAPI Docs (Optional)

To auto-generate Swagger docs:

1. Install `drf-yasg`:

```bash
pip install drf-yasg
```

2. Add to `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...,
    'drf_yasg',
]
```

3. Add Swagger URLs in `urls.py`:

```python
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="Kitchen API",
      default_version='v1',
      description="API docs for The Kitchen Project",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
```

Access Swagger at: [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/) or Redoc at `/redoc/`
