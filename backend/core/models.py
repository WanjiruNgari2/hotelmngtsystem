from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User Model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('onsite_customer', 'Onsite Customer'),
        ('online_customer', 'Online Customer'),
        ('waiter', 'Waiter'),
        ('delivery', 'Delivery Personnel'),
        ('cook', 'Cook'),
        ('cleaner', 'Cleaner'),
        ('receptionist', 'Receptionist'),
        ('manager', 'Manager'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='online_customer')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

# Meal Model
class Meal(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='meals/', blank=True, null=True)

    def __str__(self):
        return self.name

# Order Model
class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role__in': ['onsite_customer', 'online_customer']})
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    is_delivery = models.BooleanField(default=False)
    tip = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    rating = models.PositiveIntegerField(null=True, blank=True)  # optional 1–5 stars

    def __str__(self):
        return f"Order #{self.id} - {self.meal.name} by {self.customer.username}"
