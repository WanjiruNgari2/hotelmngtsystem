from rest_framework import serializers
from .models import Meal, Feedback, ClockInRecord



class ClockInRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClockInRecord
        fields = '__all__'
        read_only_fields = ['waiter', 'clock_in_time']


class MealWithFeedbackSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField(read_only=True)
    top_feedback = serializers.SerializerMethodField(read_only=True)

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

class FeedbackSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    comment = serializers.CharField(required=False)
    tip = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)

    class Meta:
        model = Feedback
        fields = ['id', 'meal', 'rating', 'tip', 'comment', 'customer_name', 'created_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['id', 'name', 'description', 'price', 'image', 'category', 'is_available']