from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, WaiterProfile

# @receiver(post_save, sender=User)
# def create_waiter_profile(sender, instance, created, **kwargs):
#     if created and instance.role == 'waiter':
#         WaiterProfile.objects.create(user=instance)
