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

]
