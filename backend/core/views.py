# Django Core
from rest_framework import filters  
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend


# DRF
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

# Local Models
from .models import User, Meal, Order, WaiterProfile, Feedback, ClockInRecord, DeliveryPersonnelProfile, ReceptionistProfile, ShiftRoster, CRMCallLog
from .forms import MealForm, FeedbackForm
from .serializers import (
    FeedbackSerializer, 
    MealWithFeedbackSerializer, 
    MealSerializer, ReceptionistProfileSerializer, CRMCallLogSerializer, ShiftRosterSerializer,
    ClockInRecordSerializer,
    DeliveryProfileSerializer
)

# ======================
# API VIEWS (DRF)
# ======================

# Delivery Signup
class DeliveryPersonnelProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.deliverypersonnelprofile
        serializer = DeliveryProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = request.user.deliverypersonnelprofile
        serializer = DeliveryProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_delivery_person(request):
    user = User.objects.create_user(
        email=request.data['email'],
        password=request.data['password'],
        role='delivery'
    )
    DeliveryPersonnelProfile.objects.create(
        user=user,
        transport_method=request.data.get('transport_method', 'bike')
    )
    return Response({"message": "Delivery personnel registered successfully."}, status=201)

# Clock Management
class ClockInView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'waiter':
            return Response({'error': 'Only waiters can clock in'}, status=403)

        active_shift = ClockInRecord.objects.filter(waiter=request.user, clock_out_time__isnull=True).first()
        if active_shift:
            return Response({'error': 'Already clocked in. Please clock out first.'}, status=400)

        record = ClockInRecord.objects.create(waiter=request.user)
        return Response({'message': 'Clock-in successful'}, status=201)

class ClockOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'waiter':
            return Response({'error': 'Only waiters can clock out'}, status=403)

        active_shift = ClockInRecord.objects.filter(waiter=request.user, clock_out_time__isnull=True).first()
        if not active_shift:
            return Response({'error': 'No active shift to clock out from'}, status=400)

        active_shift.clock_out_time = timezone.now()
        active_shift.save()
        return Response({'message': 'Clock-out successful'}, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_shifts(request):
    active_shifts = ClockInRecord.objects.filter(
        waiter=request.user,
        clock_out_time__isnull=True
    )
    serializer = ClockInRecordSerializer(active_shifts, many=True)
    return Response(serializer.data)

# Orders
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    if request.user.role not in ['online_customer', 'onsite_customer']:
        return Response({'error': 'Only customers can place orders'}, status=403)

    meal_id = request.data.get('meal_id')
    try:
        meal = Meal.objects.get(id=meal_id)
    except Meal.DoesNotExist:
        return Response({'error': 'Meal not found'}, status=404)

    order = Order.objects.create(
        customer=request.user,
        meal=meal,
        is_delivery=request.user.role == 'online_customer'
    )
    return Response({'message': 'Order placed successfully', 'order_id': order.id}, status=201)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_orders(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    data = [
        {
            'id': o.id,
            'meal': o.meal.name,
            'status': o.status,
            'created_at': o.created_at,
            'tip': getattr(o.feedback, 'tip', 0)
        } for o in orders
    ]
    return Response(data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_order_delivered(request, order_id):
    try:
        order = Order.objects.get(id=order_id, delivery_person=request.user)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found or not assigned to you'}, status=404)

    order.status = 'delivered'
    order.save()
    return Response({'message': 'Order marked as delivered'})

# Feedback
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_feedback(request, order_id):
    try:
        order = Order.objects.get(id=order_id, customer=request.user)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)

    if order.status != 'delivered':
        return Response({'error': 'Cannot leave feedback until order is delivered'}, status=400)

    serializer = FeedbackSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(order=order)
        return Response({'message': 'Feedback submitted successfully'})
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def meal_feedback(request, meal_id):
    feedbacks = Feedback.objects.filter(meal_id=meal_id)
    serializer = FeedbackSerializer(feedbacks, many=True)
    return Response(serializer.data)


class IsReceptionistOrAdmin(permissions.BasePermission):
    """
    Allow access if user is a receptionist accessing their own data
    or if the user is an admin.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        elif request.user.role == 'receptionist':
            return obj.user == request.user
        return False


class ReceptionistProfileViewSet(viewsets.ModelViewSet):
    queryset = ReceptionistProfile.objects.all()
    serializer_class = ReceptionistProfileSerializer
    permission_classes = [IsReceptionistOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['gender']
    search_fields = ['user__email', 'user__full_name']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return ReceptionistProfile.objects.all()
        elif user.role == 'receptionist':
            return ReceptionistProfile.objects.filter(user=user)
        return ReceptionistProfile.objects.none()


class ShiftRosterViewSet(viewsets.ModelViewSet):
    queryset = ShiftRoster.objects.all()
    serializer_class = ShiftRosterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return ShiftRoster.objects.all()
        elif user.role == 'receptionist':
            return ShiftRoster.objects.filter(receptionist__user=user)
        return ShiftRoster.objects.none()


class CRMCallLogViewSet(viewsets.ModelViewSet):
    queryset = CRMCallLog.objects.all()
    serializer_class = CRMCallLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return CRMCallLog.objects.all()
        elif user.role == 'receptionist':
            return CRMCallLog.objects.filter(receptionist__user=user)
        return CRMCallLog.objects.none()


# Proof of Delivery Upload
class UploadProofView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, delivery_person=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found or not assigned to you'}, status=404)

        serializer = FeedbackSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Proof uploaded successfully'})
        return Response(serializer.errors, status=400)

# Admin Reports
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def role_report_view(request):
    if request.user.role != 'admin':
        return Response({"error": "Access denied"}, status=403)

    role = request.GET.get('role')
    if role not in dict(User.ROLE_CHOICES):
        return Response({"error": "Invalid role"}, status=400)

    users = User.objects.filter(role=role)
    data = []

    for user in users:
        user_orders = Order.objects.filter(customer=user)
        total_orders = user_orders.count()
        total_tips = user_orders.aggregate(total=models.Sum('feedback__tip'))['total'] or 0

        data.append({
            "name": user.get_full_name(),
            "email": user.email,
            "total_orders": total_orders,
            "total_tips": float(total_tips),
        })

    return Response({
        "role": role,
        "user_count": users.count(),
        "report": data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_stats_view(request):
    if request.user.role != 'admin':
        return Response({"error": "Access denied"}, status=403)

    total_users = User.objects.count()
    users_by_role = User.objects.values('role').order_by().annotate(count=models.Count('id'))
    user_roles_dict = {item['role']: item['count'] for item in users_by_role}

    total_orders = Order.objects.count()
    total_meals = Meal.objects.count()
    total_feedback = Feedback.objects.count()
    total_tips = Feedback.objects.aggregate(total=models.Sum('tip'))['total'] or 0

    return Response({
        "total_users": total_users,
        "users_by_role": user_roles_dict,
        "total_orders": total_orders,
        "total_meals": total_meals,
        "total_feedback": total_feedback,
        "total_tips": f"{total_tips:.2f}"
    })

# Meal Availability Toggle
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def toggle_meal_availability_patch(request, pk):
    if request.user.role != 'waiter':
        return Response({"error": "Access denied"}, status=403)

    try:
        meal = Meal.objects.get(pk=pk)
    except Meal.DoesNotExist:
        return Response({"error": "Meal not found"}, status=404)

    serializer = MealSerializer(meal, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Availability updated", "meal": serializer.data})
    return Response(serializer.errors, status=400)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def toggle_meal_availability(request, meal_id):
    user = request.user
    if user.role not in ['waiter', 'cook', 'manager', 'admin']:
        return Response({'error': 'Not authorized to toggle meals.'}, status=403)

    try:
        meal = Meal.objects.get(id=meal_id)
        meal.is_available = not meal.is_available
        meal.save()
        return Response({'message': 'Meal availability toggled.', 'is_available': meal.is_available})
    except Meal.DoesNotExist:
        return Response({'error': 'Meal not found.'}, status=404)

@api_view(['GET'])
def public_menu(request):
    meals = Meal.objects.filter(is_available=True)
    serializer = MealSerializer(meals, many=True)
    return Response(serializer.data)

# ======================
# LEGACY TEMPLATE VIEWS (Template-based)
# ======================

# Authentication Views
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            # Redirect based on user role
            if user.role == 'admin':
                return redirect('admin_orders')
            elif user.role == 'waiter':
                return redirect('waiter_dashboard')
            elif user.role in ['onsite_customer', 'online_customer']:
                return redirect('customer_dashboard')
            elif user.role == 'delivery':
                return redirect('delivery_dashboard')
            else:
                messages.error(request, "Unknown user role.")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# Customer Views
@login_required
def customer_dashboard(request):
    return render(request, 'core/dashboard_customer.html')


@login_required
def meal_list_view(request):
    if request.user.role not in ['online_customer', 'onsite_customer']:
        return redirect('login')
    meals = Meal.objects.filter(is_available=True)
    return render(request, 'core/meal_list.html', {'meals': meals})


@login_required
def place_order(request, meal_id):
    if request.method == 'POST' and request.user.role in ['online_customer', 'onsite_customer']:
        meal = get_object_or_404(Meal, id=meal_id)
        Order.objects.create(
            customer=request.user,
            meal=meal,
            is_delivery=(request.user.role == 'online_customer'),
        )
        return redirect('my_orders')
    return redirect('meal_list')


@login_required
def my_orders_view(request):
    if request.user.role not in ['online_customer', 'onsite_customer']:
        return redirect('login')
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    paginator = Paginator(orders, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/my_orders.html', {'page_obj': page_obj})


@login_required
def leave_feedback(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    if order.status != 'delivered':
        return redirect('my_orders')
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.customer = request.user
            feedback.order = order
            feedback.meal = order.meal
            feedback.save()
            return redirect('my_orders')
    else:
        form = FeedbackForm()
    return render(request, 'core/leave_feedback.html', {'form': form, 'order': order})


# Admin Views
@staff_member_required
def admin_orders_view(request):
    orders = Order.objects.all().order_by('-created_at')

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        order = get_object_or_404(Order, id=order_id)
        order.status = new_status
        order.save()
        return redirect('admin_orders')

    return render(request, 'core/admin_orders.html', {'orders': orders})


@staff_member_required
def admin_meals_view(request):
    meals = Meal.objects.all().order_by('-id')
    return render(request, 'core/admin_meals.html', {'meals': meals})


@staff_member_required
def add_meal_view(request):
    if request.method == 'POST':
        form = MealForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_meals')
    else:
        form = MealForm()
    return render(request, 'core/meal_form.html', {'form': form, 'title': 'Add Meal'})


@staff_member_required
def edit_meal_view(request, meal_id):
    meal = get_object_or_404(Meal, id=meal_id)
    if request.method == 'POST':
        form = MealForm(request.POST, request.FILES, instance=meal)
        if form.is_valid():
            form.save()
            return redirect('admin_meals')
    else:
        form = MealForm(instance=meal)
    return render(request, 'core/meal_form.html', {'form': form, 'title': 'Edit Meal'})


@staff_member_required
def delete_meal_view(request, meal_id):
    meal = get_object_or_404(Meal, id=meal_id)
    meal.delete()
    return redirect('admin_meals')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def waiter_dashboard(request):
    if request.user.role != 'waiter':
        return Response({"error": "Access denied"}, status=403)

    meals = Meal.objects.all()
    serializer = MealWithFeedbackSerializer(meals, many=True)
    return Response(serializer.data)



@action(detail=False, methods=['get'])
def me(self, request):
    profile = ReceptionistProfile.objects.get(user=request.user)
    serializer = self.get_serializer(profile)
    return Response(serializer.data)
