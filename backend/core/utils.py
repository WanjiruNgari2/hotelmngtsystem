# core/utils.py

from datetime import date
from django.contrib.sessions.models import Session

def is_customer_birthday(birthday):
    """Returns True if today is the customer's birthday."""
    if not birthday:
        return False
    today = date.today()
    return birthday.day == today.day and birthday.month == today.month

def get_client_ip(request):
    """Gets the IP address of the client."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def remember_customer_session(request, customer_id):
    """Stores customer ID in session for personalization."""
    request.session['customer_id'] = customer_id

def get_remembered_customer(request):
    """Returns the remembered customer ID if available."""
    return request.session.get('customer_id')

def was_greeted_today(request):
    """Prevents repeating birthday greeting or welcome message in one day."""
    last_greet_date = request.session.get('last_greet_date')
    today_str = date.today().isoformat()
    if last_greet_date == today_str:
        return True
    request.session['last_greet_date'] = today_str
    return False
