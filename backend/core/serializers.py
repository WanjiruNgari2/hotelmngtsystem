from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Meal, Order, Feedback, ClockInRecord, ShiftRoster,ReceptionistProfile,
    DeliveryPersonnelProfile, OnsiteCustomerProfile, 
    ProofOfDelivery, CRMCallLog , OnlineCustomerProfile  
)

User = get_user_model()

# ----------------------
# User Serializer
# ----------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

# ----------------------
# Delivery Profile
# ----------------------
class DeliveryProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = DeliveryPersonnelProfile
        fields = [
            'user',
            'profile_picture',
            'transport_method',
            'current_location',
            'upvotes',
            'tips_earned'
        ]
        read_only_fields = ['upvotes', 'tips_earned']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['role'] = 'delivery'
        user = User.objects.create_user(**user_data)
        profile = DeliveryPersonnelProfile.objects.create(user=user, **validated_data)
        return profile

# ----------------------
# Clock In / Out
# ----------------------
class ClockInRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClockInRecord
        fields = '__all__'
        read_only_fields = ['waiter', 'clock_in_time']

# ----------------------
# Meal + Feedback
# ----------------------
class MealWithFeedbackSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    top_feedback = serializers.SerializerMethodField()

    class Meta:
        model = Meal
        fields = ['id', 'name', 'description', 'price', 'average_rating', 'top_feedback']

    def get_average_rating(self, meal):
        feedbacks = Feedback.objects.filter(meal=meal)
        if feedbacks.exists():
            return round(sum(f.rating for f in feedbacks) / feedbacks.count(), 2)
        return None

    def get_top_feedback(self, meal):
        feedbacks = Feedback.objects.filter(meal=meal).order_by('-created_at')[:3]
        return [f"{f.customer.username}: {f.comment}" for f in feedbacks if f.comment]

# ----------------------
# Feedback
# ----------------------
class FeedbackSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    comment = serializers.CharField(required=False)
    tip = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)

    class Meta:
        model = Feedback
        fields = '__all__'

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

# ----------------------
# Meals
# ----------------------
class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['id', 'name', 'description', 'price', 'image', 'category', 'is_available']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

# ----------------------
# Proof of Delivery Upload
# ----------------------
class ProofOfDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProofOfDelivery
        fields = ['id', 'order', 'image', 'uploaded_at']
        read_only_fields = ['uploaded_at']


#ReceptionistProfileSerializer
class ReceptionistProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = ReceptionistProfile
        fields = [
            'id', 'email', 'full_name', 'profile_picture',
            'gender', 'clock_in_time', 'clock_out_time',
        ]


# ShiftRosterSerializer
class ShiftRosterSerializer(serializers.ModelSerializer):
    receptionist_name = serializers.CharField(source='receptionist.user.full_name', read_only=True)

    class Meta:
        model = ShiftRoster
        fields = [
            'id', 'receptionist', 'receptionist_name',
            'shift_date', 'shift_start', 'shift_end', 'is_on_duty',
        ]

#CRMCallLogSerializer
class CRMCallLogSerializer(serializers.ModelSerializer):
    receptionist_name = serializers.CharField(source='receptionist.user.full_name', read_only=True)

    class Meta:
        model = CRMCallLog
        fields = [
            'id', 'receptionist', 'receptionist_name',
            'customer_name', 'phone_number', 'reason_for_call',
            'follow_up_date', 'created_at', 'call_time','notes',
        ]

#Online customer
class OnlineCustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineCustomerProfile
        fields = '__all__'

#onsite customer
class OnsiteCustomerProfileSerializer(serializers.ModelSerializer):
    waiter_name = serializers.SerializerMethodField()

    class Meta:
        model = OnsiteCustomerProfile
        fields = '__all__'
        read_only_fields = ['user', 'joined_at']

    def get_waiter_name(self, obj):
        return obj.waiter.full_name if obj.waiter else None
