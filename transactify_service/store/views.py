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


@login_required
def dashboard(request):
    sites = [
            {"name": "Don Knabberello", "url": f"/{settings.STORE_NAME}/customers/", 
             'description':"Management of the Don Knabberello Store", 
             'icon_link': "#home",
             'goto_text': "Go to Store"},
            {"name": "User Management (Under Construction)", "url": f"/{settings.STORE_NAME}/customers/", 
             'description':"Management of the Don Knabberello Store", 
             'icon_link': "#people-circle",
             'goto_text': "Access"},
             {"name": "Admin Area", "url": f"/{settings.STORE_NAME}/admin/", 
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