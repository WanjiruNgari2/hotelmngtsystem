from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/admin/orders/', views.admin_orders_view, name='admin_orders'),
    path('meals/', views.meal_list_view, name='meal_list'),
    path('meals/order/<int:meal_id>/', views.place_order, name='place_order'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
# Admin Meal URLs
    path('dashboard/admin/meals/', views.admin_meals_view, name='admin_meals'),
    path('dashboard/admin/meals/add/', views.add_meal_view, name='add_meal'),
    path('dashboard/admin/meals/<int:meal_id>/edit/', views.edit_meal_view, name='edit_meal'),
    path('dashboard/admin/meals/<int:meal_id>/delete/', views.delete_meal_view, name='delete_meal'),

]
