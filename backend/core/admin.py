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
    ShiftRoster,
    CRMCallLog,
    OnlineCustomerProfile,
    OnsiteCustomerProfile,
    ProofOfDelivery
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'is_active')
    list_filter = ('role',)
    search_fields = ('email',)

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_available']
    list_filter = ['is_available']
    search_fields = ['name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'meal', 'status', 'created_at')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "customer":
            kwargs["queryset"] = User.objects.filter(role__in=['onsite_customer', 'online_customer'])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('order', 'rating', 'tip', 'created_at')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "customer":
            kwargs["queryset"] = User.objects.filter(role__in=['onsite_customer', 'online_customer'])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(WaiterProfile)
class WaiterProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "age", "gender", "table_assigned", "total_tips", "votes_received"]  # ✅
    readonly_fields = ['get_total_tips', 'age', 'gender', 'get_votes']

    def get_total_tips(self, obj):
        return obj.total_tips() 
    get_total_tips.short_description = "Total Tips"

    def get_votes(self, obj):
        return obj.votes_received() 
    get_votes.short_description = "Votes"


@admin.register(ClockInRecord)
class ClockInAdmin(admin.ModelAdmin):
    list_display = ['user', 'clock_in_time', 'clock_out_time']
    list_filter = ['user']

@admin.register(DeliveryPersonnelProfile)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['user', 'transport_method', 'current_location']
    raw_id_fields = ('user',)
    search_fields = ['user__email']

@admin.register(ReceptionistProfile)
class ReceptionistProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'clock_in_time', 'clock_out_time')
    raw_id_fields = ('user',)
    search_fields = ('user__email',)

@admin.register(ShiftRoster)
class ShiftRosterAdmin(admin.ModelAdmin):
    list_display = ('receptionist', 'shift_date', 'shift_start', 'shift_end', 'is_on_duty')
    list_filter = ('receptionist',)

@admin.register(CRMCallLog)
class CRMCallLogAdmin(admin.ModelAdmin):
    list_display = ('receptionist', 'call_time', 'customer_name', 'reason_for_call')
    list_filter = ('call_time',)
    search_fields = ('customer_name',)
    exclude = ('notes',)

@admin.register(OnlineCustomerProfile)
class OnlineCustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'location', 'member_since']
    search_fields = ['user__email', 'full_name', 'location']

@admin.register(OnsiteCustomerProfile)
class OnsiteCustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'table_number', 'waiter', 'joined_at']
    search_fields = ['full_name', 'table_number']
    list_filter = ['gender', 'waiter']

@admin.register(ProofOfDelivery)
class ProofOfDeliveryAdmin(admin.ModelAdmin):
    list_display = ['order', 'uploaded_at']
    search_fields = ['order__id']
