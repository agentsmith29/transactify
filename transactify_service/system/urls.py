from django.urls import path
from .views import shutdown_system, reboot_system


urlpatterns = [
    # System Management
    path("shutdown/", shutdown_system, name="shutdown_system"),
    path("reboot/", reboot_system, name="reboot_system"),
]