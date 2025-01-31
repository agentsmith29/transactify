
import os
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.template import loader

from django.contrib.auth.models import User
from transactify_service.settings import CONFIG




#@login_required
def store_selection(request):
    # Replace this with actual store data from the database
    stores = [
        {"name": "Store 1", "url": "/store1/"},
        {"name": "Store 2", "url": "/store2/"},
        {"name": "Store 3", "url": "/store3/"},
    ]
    return render(request, 'dashboard.html', {"stores": stores})


@login_required
def dashboard(request):
    #template = loader.get_template("store/dashboard.html")
    #return HttpResponse(template.render({}, request))
    sites = [
            {"name": "Don Knabberello", "url": f"/{CONFIG.webservice.SERVICE_NAME}/summary/", 
             'description':"Management of the Don Knabberello Store", 
             'icon_link': "#home",
             'goto_text': "Go to Store"},
            {"name": "User Management (Under Construction)", "url": f"/{CONFIG.webservice.SERVICE_NAME}/summary/", 
             'description':"Management of the Don Knabberello Store", 
             'icon_link': "#people-circle",
             'goto_text': "Access"},
             {"name": "Admin Area", "url": f"/{CONFIG.webservice.SERVICE_NAME}/admin/", 
             'description':"Admin Area", 
             'icon_link': "#gear-fill",
             'goto_text': "Access"},
            ]
    user = request.user
    if user.groups.filter(name='Admins').exists():
        return redirect('/admin/')
    elif user.groups.filter(name='Owner').exists():
        return render(request, 'dashboard.html', {"entries": sites})
    elif user.groups.filter(name='Manager').exists():
        return render(request, 'dashboard.html', {"entries": sites})
    elif user.groups.filter(name='Customer').exists():
        return render(request, 'dashboard.html', {"entries": sites})
    else:
        return render(request, 'dashboard.html', {"entries": sites})
        #return render(request, 'dashboard.html')
        return redirect('/')
    

def custom_csrf_failure_view(request, reason=""):
    """
    Custom view to handle CSRF failures.
    """
    context = {
        'message': "CSRF verification failed. Please try again.",
        'reason': reason,
    }
    return render(request, "csrf_failure.html", context, status=403)