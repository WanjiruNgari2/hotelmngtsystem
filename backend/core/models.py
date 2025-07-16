from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


#clockInRecord
class ClockInRecord(models.Model):
    waiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    clock_in_time = models.DateTimeField(default=timezone.now)
    clock_out_time = models.DateTimeField(null=True, blank=True)

    def is_active(self):
        return self.clock_out_time is None

    def __str__(self):
        return f"{self.waiter.get_full_name()} - {self.clock_in_time} to {self.clock_out_time or 'Present'}"

    def save(self, *args, **kwargs):
            # Prevent active shifts > 12 hours
            if self.clock_out_time is None:
                max_duration = timedelta(hours=12)
                if timezone.now() - self.clock_in_time > max_duration:
                    self.clock_out_time = self.clock_in_time + max_duration
            super().save(*args, **kwargs)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')  # You can adjust this

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

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
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()  # 👈 connect the manager here

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"



#waiter profile
class WaiterProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=50, unique=True)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    clock_in_time = models.DateTimeField(null=True, blank=True)
    clock_out_time = models.DateTimeField(null=True, blank=True)

    def hours_worked(self):
        if self.clock_in_time and self.clock_out_time:
            return self.clock_out_time - self.clock_in_time
        return None

    def __str__(self):
        return f"Waiter: {self.user.username}"

# Meal Model
class Meal(models.Model):
    CATEGORY_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
        ('drink', 'Drink'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='meals/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='lunch')  # ✅ New

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
    rating = models.PositiveIntegerField(null=True, blank=True)
    review = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.meal.name} by {self.customer.username}"


#feedback model
class Feedback(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    tip = models.DecimalField(max_digits=6, decimal_places=2)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
