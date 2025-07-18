from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from .views import (
    # Meal & Menu
    public_menu,
    toggle_meal_availability,
    toggle_meal_availability_patch,
    meal_feedback, AvailableMealListView,

    # Order & Feedback
    place_order,
    my_orders,
    mark_order_delivered,
    leave_feedback, FeedbackCreateView,

    # Admin Stats & Reports
    login_view,
    admin_stats_view,
    role_report_view,
    admin_orders_view,

    # Waiter & Clock
    waiter_dashboard,
    ClockInView,
    ClockOutView,

    # Delivery
    register_delivery_person,
    DeliveryPersonnelProfileView,
    UploadProofView, ChangeDeliveryPersonView,

    # Receptionist
    ReceptionistProfileViewSet, 
    ShiftRosterViewSet, 
    CRMCallLogViewSet,

    # Online Customer
    OnlineCustomerProfileListCreateView, customer_order_history, give_feedback, change_delivery_person,
    OnlineCustomerProfileDetailView, CustomerOrderHistoryView,

     #onsite customer
     OnsiteCustomerProfileViewSet
)

router = DefaultRouter()
router.register(r'receptionists', ReceptionistProfileViewSet, basename='receptionists')
router.register(r'shift-rosters', ShiftRosterViewSet, basename='shift-rosters')
router.register(r'crm-calls', CRMCallLogViewSet, basename='crm-calls')
router.register(r'onsite-customers', OnsiteCustomerProfileViewSet, basename='onsite-customer')


urlpatterns = [
    # Auth
    path('api/token/', obtain_auth_token, name='api_token_auth'),

    # Menu
    path('api/menu/', public_menu, name='public_menu'),
    path('api/meals/<int:meal_id>/feedback/', meal_feedback, name='meal_feedback'),
    path('api/meals/<int:meal_id>/toggle/', toggle_meal_availability, name='toggle_meal_availability'),
    path('api/meals/<int:pk>/patch-availability/', toggle_meal_availability_patch, name='toggle_patch'),
    
    # Orders
     path('api/orders/place/', place_order, name='place_order'),
     path('api/orders/my/', my_orders, name='my_orders'),
     path('api/orders/<int:order_id>/delivered/', mark_order_delivered, name='mark_delivered'),
     path('api/orders/<int:order_id>/change-delivery/', ChangeDeliveryPersonView.as_view(), name='change-delivery-person'),
     path('orders/history/', customer_order_history, name='order-history'),
     path('orders/<int:order_id>/feedback/', give_feedback, name='give-feedback'),
     path('orders/<int:order_id>/change-delivery/', change_delivery_person, name='change-delivery'),

    # Feedback
    path('api/orders/<int:order_id>/feedback/', leave_feedback, name='leave_feedback'),
    path('api/feedback/', FeedbackCreateView.as_view(), name='submit-feedback'),

    # Admin
    path('api/admin/stats/', admin_stats_view, name='admin_stats'),
    path('dashboard/admin/orders/', admin_orders_view, name='admin_orders'),
    path('api/admin/reports/', role_report_view, name='role_report'),

    # Waiter
    path('api/waiter/dashboard/', waiter_dashboard, name='waiter_dashboard'),
    path('api/waiter/clock-in/', ClockInView.as_view(), name='clock_in'),
    path('api/waiter/clock-out/', ClockOutView.as_view(), name='clock_out'),

    # Delivery
    path('api/delivery/register/', register_delivery_person, name='register_delivery'),
    path('api/delivery/profile/', DeliveryPersonnelProfileView.as_view(), name='delivery_profile'),
    path('api/delivery/orders/<int:order_id>/upload-proof/', UploadProofView.as_view(), name='upload_proof'),

    # Receptionist
    path('api/', include(router.urls)),

    # Online Customer
    path('api/online-customers/', OnlineCustomerProfileListCreateView.as_view(), 
         name='online-customer-list-create'),
    path('api/online-customers/<int:pk>/', OnlineCustomerProfileDetailView.as_view(), 
         name='online-customer-detail'),
    path('api/customer/orders/history/', CustomerOrderHistoryView.as_view(), 
         name='customer-order-history'),
    path('api/meals/available/', AvailableMealListView.as_view(),
          name='available-meals'),

]