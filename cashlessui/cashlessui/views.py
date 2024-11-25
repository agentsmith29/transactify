from django.contrib.auth.decorators import login_required
from django.shortcuts import render

#@login_required
def store_selection(request):
    # Replace this with actual store data from the database
    stores = [
        {"name": "Store 1", "url": "/store1/"},
        {"name": "Store 2", "url": "/store2/"},
        {"name": "Store 3", "url": "/store3/"},
    ]
    return render(request, 'store_selection.html', {"stores": stores})
