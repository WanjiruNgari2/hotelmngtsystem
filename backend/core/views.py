from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator

from .models import Meal, Order
from .forms import MealForm, FeedbackForm


# LOGIN VIEW
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Redirect by role
            if user.role in ['onsite_customer', 'online_customer']:
                return redirect('customer_dashboard')
            elif user.role == 'waiter':
                return redirect('waiter_dashboard')
            elif user.role == 'admin':
                return redirect('/admin/')
            else:
                return redirect('default_dashboard')  # fallback
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})


# LOGOUT
def logout_view(request):
    logout(request)
    return redirect('login')


# CUSTOMER DASHBOARD
@login_required
def customer_dashboard(request):
    return render(request, 'core/dashboard_customer.html')


# VIEW MEALS (Customer)
@login_required
def meal_list_view(request):
    if request.user.role not in ['online_customer', 'onsite_customer']:
        return redirect('login')
    meals = Meal.objects.all()
    return render(request, 'core/meal_list.html', {'meals': meals})


# PLACE ORDER
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


# CUSTOMER ORDER HISTORY
@login_required
def my_orders_view(request):
    if request.user.role not in ['online_customer', 'onsite_customer']:
        return redirect('login')

    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    paginator = Paginator(orders, 5)  # Show 5 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/my_orders.html', {'page_obj': page_obj})


# LEAVE FEEDBACK
@login_required
def leave_feedback(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)

    if order.status != 'delivered':
        return redirect('my_orders')  # Only allow feedback after delivery

    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('my_orders')
    else:
        form = FeedbackForm(instance=order)

    return render(request, 'core/leave_feedback.html', {'form': form, 'order': order})


# ADMIN DASHBOARD: VIEW ORDERS
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


# ADMIN: VIEW MEALS
@staff_member_required
def admin_meals_view(request):
    meals = Meal.objects.all().order_by('-id')
    return render(request, 'core/admin_meals.html', {'meals': meals})


# ADMIN: ADD MEAL
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


# ADMIN: EDIT MEAL
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


# ADMIN: DELETE MEAL
@staff_member_required
def delete_meal_view(request, meal_id):
    meal = get_object_or_404(Meal, id=meal_id)
    meal.delete()
    return redirect('admin_meals')
