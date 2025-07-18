# core/admin.py
from django.contrib import admin
from .models import (
    User,
    Meal,
    Order,
    WaiterProfile,
    Feedback,
    ClockInRecord,
    DeliveryPersonnelProfile,
    ReceptionistProfile,
    ShiftRoster, OnlineCustomerProfile,
    CRMCallLog, OnsiteCustomerProfile
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'is_active')
    list_filter = ('role',)
    search_fields = ('email',)

@admin.register(ReceptionistProfile)
class ReceptionistProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender')
    raw_id_fields = ('user',)
    search_fields = ('user__email',)

@admin.register(ShiftRoster)
class ShiftRosterAdmin(admin.ModelAdmin):
    list_display = ('receptionist', 'shift_start', 'shift_end')
    list_filter = ('receptionist',)

@admin.register(CRMCallLog)
class CRMCallLogAdmin(admin.ModelAdmin):
    list_display = ('receptionist', 'call_time', 'customer_name')
    list_filter = ('call_time',)
    search_fields = ('customer_name', 'notes')

admin.site.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['order', 'rating', 'tip_amount', 'created_at']


@admin.register(OnsiteCustomerProfile)
class OnsiteCustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'table_number', 'waiter', 'joined_at']
    search_fields = ['full_name', 'table_number']
    list_filter = ['gender', 'waiter']


admin.site.register(OnlineCustomerProfile)
admin.site.register(Meal)
admin.site.register(Order)
admin.site.register(WaiterProfile)
class WaiterProfile(admin.ModelAdmin):
    list_display = ('user', 'gender', 'full_name')
    raw_id_fields = ('user',)
    search_fields = ('user__email',)

admin.site.register(ClockInRecord)
admin.site.register(DeliveryPersonnelProfile)