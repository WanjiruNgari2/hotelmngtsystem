from django.urls import path
from . import views
from .views import (
    meal_feedback, 
    waiter_dashboard,
    public_menu, 
    toggle_meal_availability, 
    admin_stats_view, 
    role_report_view,
    ClockInView, 
    ClockOutView
)
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # HTML Template Views
    path('', views.login_view, name='login'),
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/admin/orders/', views.admin_orders_view, name='admin_orders'),
    path('meals/', views.meal_list_view, name='meal_list'),
    path('meals/order/<int:meal_id>/', views.place_order, name='place_order'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
    
    # Admin Meal Management
    path('dashboard/admin/meals/', views.admin_meals_view, name='admin_meals'),
    path('dashboard/admin/meals/add/', views.add_meal_view, name='add_meal'),
    path('dashboard/admin/meals/<int:meal_id>/edit/', views.edit_meal_view, name='edit_meal'),
    path('dashboard/admin/meals/<int:meal_id>/delete/', views.delete_meal_view, name='delete_meal'),
    path('my-orders/<int:order_id>/feedback/', views.leave_feedback, name='leave_feedback'),

    # API Endpoints
    path('api/menu/', public_menu, name='public_menu'),
    path('api/admin/stats/', admin_stats_view, name='admin_stats'),
    path('api/admin/reports/', role_report_view, name='role_report'),
    path('api/meals/<int:meal_id>/feedback/', meal_feedback, name='meal-feedback'),
    path('api-token-auth/', obtain_auth_token),
    path('api/waiter/dashboard/', waiter_dashboard, name='waiter_dashboard'),
    path('api/waiter/meals/<int:meal_id>/toggle/', toggle_meal_availability, name='toggle_meal_availability'),
    
    # Clock In/Out (using class-based views)
    path('api/waiter/clock-in/', ClockInView.as_view(), name='clock_in'),
    path('api/waiter/clock-out/', ClockOutView.as_view(), name='clock_out'),
]