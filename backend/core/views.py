# Django Core
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Sum

# DRF
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status

# Local Models
from .models import User, Meal, Order, WaiterProfile, Feedback, ClockInRecord
from .forms import MealForm, FeedbackForm
from .serializers import (
    FeedbackSerializer, 
    MealWithFeedbackSerializer, 
    MealSerializer,
    ClockInRecordSerializer
)

# ======================
# API VIEWS (DRF)
# ======================

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
        total_tips = user_orders.aggregate(total=models.Sum('tip'))['total'] or 0

        data.append({
            "username": user.username,
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
    total_tips = Order.objects.aggregate(total=models.Sum('tip'))['total'] or 0

    return Response({
        "total_users": total_users,
        "users_by_role": user_roles_dict,
        "total_orders": total_orders,
        "total_meals": total_meals,
        "total_feedback": total_feedback,
        "total_tips": f"{total_tips:.2f}"
    })

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def toggle_meal_availability(request, pk):
    if request.user.role != 'waiter':
        return Response({"error": "Access denied"}, status=403)

    try:
        meal = Meal.objects.get(pk=pk)
    except Meal.DoesNotExist:
        return Response({"error": "Meal not found"}, status=404)

    serializer = MealAvailabilitySerializer(meal, data=request.data, partial=True)
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def waiter_dashboard(request):
    if request.user.role != 'waiter':
        return Response({"error": "Access denied"}, status=403)

    meals = Meal.objects.all()
    serializer = MealWithFeedbackSerializer(meals, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def meal_feedback(request, meal_id):
    feedbacks = Feedback.objects.filter(meal_id=meal_id)
    serializer = FeedbackSerializer(feedbacks, many=True)
    return Response(serializer.data)

# ======================
# TEMPLATE VIEWS
# ======================

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.role in ['onsite_customer', 'online_customer']:
                return redirect('customer_dashboard')
            elif user.role == 'waiter':
                return redirect('waiter_dashboard')
            elif user.role == 'admin':
                return redirect('/admin/')
            else:
                return redirect('default_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def customer_dashboard(request):
    return render(request, 'core/dashboard_customer.html')

@login_required
def meal_list_view(request):
    if request.user.role not in ['online_customer', 'onsite_customer']:
        return redirect('login')
    meals = Meal.objects.all()
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
        form = FeedbackForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('my_orders')
    else:
        form = FeedbackForm(instance=order)

    return render(request, 'core/leave_feedback.html', {'form': form, 'order': order})

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