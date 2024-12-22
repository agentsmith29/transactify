from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings

#@login_required
def store_selection(request):
    # Replace this with actual store data from the database
    stores = [
        {"name": "Store 1", "url": "/store1/"},
        {"name": "Store 2", "url": "/store2/"},
        {"name": "Store 3", "url": "/store3/"},
    ]
    return render(request, 'dashboard.html', {"stores": stores})



def custom_csrf_failure_view(request, reason=""):
    """
    Custom view to handle CSRF failures.
    """
    context = {
        'message': "CSRF verification failed. Please try again.",
        'reason': reason,
    }
    return render(request, "csrf_failure.html", context, status=403)