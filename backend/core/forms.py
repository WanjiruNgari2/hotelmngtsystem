from django import forms
from .models import Meal, Order


class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['name', 'description', 'price', 'image']


from django import forms
from .models import Order

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['rating', 'tip', 'review']

        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1,
                'max': 5,
                'placeholder': 'Rating (1–5)',
                'class': 'w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'tip': forms.NumberInput(attrs={
                'placeholder': 'Tip (Ksh)',
                'class': 'w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'review': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write your review here...',
                'class': 'w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
        }
