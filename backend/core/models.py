from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
# ========================
# Custom UserManager Model
# ========================
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role='onsite_customer', **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('waiter', 'Waiter'),
        ('onsite_customer', 'Onsite Customer'),
        ('online_customer', 'Online Customer'),
        ('delivery', 'Delivery Personnel'),
        ('receptionist', 'Receptionist'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    objects = UserManager()

    def __str__(self):
        return self.email
    
# ========================
# Meal Model
# ========================
class Meal(models.Model):
    CATEGORY_CHOICES = [
        ('main', 'Main Course'),
        ('drink', 'Drink'),
        ('dessert', 'Dessert'),
        ('starter', 'Starter'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='meal_images/', blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='main')
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# ========================
# Order Model
# ========================
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('delivering', 'Delivering'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_delivery = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    delivery_person = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='deliveries', limit_choices_to={'role': 'delivery'})
    proof_of_delivery = models.ImageField(upload_to='proofs/', null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.meal.name} - {self.customer.username}"


# ========================
# Feedback Model
# ========================
class Feedback(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='feedback')
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    tip = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.customer.username} - Rating {self.rating}"


# ========================
# Clock-In Records for Waiters
# ========================
class ClockInRecord(models.Model):
    waiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clock_records')
    clock_in_time = models.DateTimeField(default=timezone.now)
    clock_out_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.waiter.username} - In: {self.clock_in_time} Out: {self.clock_out_time}"


# ========================
# Delivery Profile
# ========================
class DeliveryPersonnelProfile(models.Model):
    TRANSPORT_CHOICES = [
        ('bike', 'Bike'),
        ('car', 'Car'),
        ('walk', 'On Foot'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='deliverypersonnelprofile')
    profile_picture = models.ImageField(upload_to='delivery_profiles/', null=True, blank=True)
    transport_method = models.CharField(max_length=10, choices=TRANSPORT_CHOICES, default='bike')
    current_location = models.CharField(max_length=255, blank=True)
    upvotes = models.IntegerField(default=0)
    tips_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}'s Delivery Profile"


class WaiterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"WaiterProfile: {self.user.username}"

class ProofOfDelivery(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='proof')
    image = models.ImageField(upload_to='proofs/')
    notes = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proof for Order #{self.order.id}"


class ReceptionistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, default="Receptionist User")
    profile_picture = models.ImageField(upload_to='receptionists/', blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], blank=True)
    clock_in_time = models.DateTimeField(blank=True, null=True)
    clock_out_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Receptionist: {self.user.email}"


# Duty roaster
class ShiftRoster(models.Model):
    receptionist = models.ForeignKey(ReceptionistProfile, on_delete=models.CASCADE)
    shift_date = models.DateField()
    shift_start = models.TimeField()
    shift_end = models.TimeField()
    is_on_duty = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.receptionist.user.email} shift on {self.shift_date}"

# CRM calllogs
class CRMCallLog(models.Model):
    receptionist = models.ForeignKey(ReceptionistProfile, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    call_time = models.DateTimeField(default=timezone.now)  # Make sure this exists
    notes = models.TextField(blank=True)
    reason_for_call = models.TextField()
    follow_up_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Call with {self.customer_name} at {self.call_time}"


