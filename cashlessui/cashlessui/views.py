from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect

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
    stores = [
            {"name": "Don Knabberello", "url": "/donknabberello/customers/", 
             'description':"Management of the Don Knabberello Store", 'icon_link': "#home",
             'goto_text': "Go to Store"},
            {"name": "User Management (Under Construction)", "url": "/donknabberello/customers/", 
             'description':"Management of the Don Knabberello Store", 'icon_link': "#people-circle",
             'goto_text': "Access"},
             {"name": "Admin Area", "url": "/admin/", 
             'description':"Admin Area", 'icon_link': "#gear-fill",
             'goto_text': "Access"},
            ]
    user = request.user
    if user.groups.filter(name='Admins').exists():
        return redirect('/admin/')
    elif user.groups.filter(name='Owner').exists():
        return render(request, 'dashboard.htmll', {"entries": stores})
    elif user.groups.filter(name='Manager').exists():
        return render(request, 'dashboard.html', {"entries": stores})
    elif user.groups.filter(name='Customer').exists():
        return render(request, 'dashboard.html', {"entries": stores})
    else:
        return render(request, 'dashboard.html', {"entries": stores})
        #return render(request, 'dashboard.html')
        return redirect('/')