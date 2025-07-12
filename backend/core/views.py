from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Order
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Meal
from .forms import MealForm  


#view all meals
@staff_member_required
def admin_meals_view(request):
    meals = Meal.objects.all().order_by('-id')
    return render(request, 'core/admin_meals.html', {'meals': meals})

#add Meals
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


#edit meals
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


#delete meal
@staff_member_required
def delete_meal_view(request, meal_id):
    meal = get_object_or_404(Meal, id=meal_id)
    meal.delete()
    return redirect('admin_meals')


@login_required
def place_order(request, meal_id):
    if request.method == 'POST' and request.user.role in ['online_customer', 'onsite_customer']:
        meal = Meal.objects.get(id=meal_id)
        Order.objects.create(
            customer=request.user,
            meal=meal,
            is_delivery=(request.user.role == 'online_customer'),
        )
        return redirect('my_orders')  # Redirect to "My Orders" after placing
    return redirect('meal_list')

@login_required
def meal_list_view(request):
    if request.user.role not in ['online_customer', 'onsite_customer']:
        return redirect('login')  # Block access for other roles

    meals = Meal.objects.all()
    return render(request, 'core/meal_list.html', {'meals': meals})


@staff_member_required
def admin_orders_view(request):
    orders = Order.objects.all().order_by('-created_at')

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        order = Order.objects.get(id=order_id)
        order.status = new_status
        order.save()
        return redirect('admin_orders')

    return render(request, 'core/admin_orders.html', {'orders': orders})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Redirect by role
            if user.role == 'onsite_customer' or user.role == 'online_customer':
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


@login_required
def my_orders_view(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'core/my_orders.html', {'orders': orders})


@login_required
def customer_dashboard(request):
    return render(request, 'core/dashboard_customer.html')

def logout_view(request):
    logout(request)
    return redirect('login')

