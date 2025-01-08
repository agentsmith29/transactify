"""
URL configuration for transactify_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.contrib import admin
from django.urls import path
from django.urls import include, path
from django.conf import settings

#from django.contrib.auth.views import LoginView, LogoutView
from transactify_service.webviews.LoginView import LoginView, LogoutView  
from django.contrib.auth import views as auth_views

from transactify_service.views import health_check
import store.StoreLogsDBHandler 



SERVICE_NAME = settings.CONFIG.webservice.SERVICE_NAME
logger = store.StoreLogsDBHandler.setup_custom_logging("transactify_service")
logger.info(f"Service Name: {SERVICE_NAME}")
urlpatterns = [
    path(f'{SERVICE_NAME}/login/', LoginView.as_view(template_name='login.html'), name='login'),
    path(f'{SERVICE_NAME}/logout/', LogoutView.as_view(), name='logout'),
    path(f'{SERVICE_NAME}/admin/', admin.site.urls),

    path(f'{SERVICE_NAME}/', include("store.urls")),
    path(f'{SERVICE_NAME}/api/', include("api.urls")),

    path(f'{SERVICE_NAME}/health/', health_check),
]
