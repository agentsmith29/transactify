from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import subprocess
import os
import traceback

# Create your views here.
# Helper function to check if the user is a staff member
def is_admin_user(user: User, group_name: str = "admin") -> bool:
    # Check if user is in group Admin
    print(f"User is admin {user.groups.filter(name=group_name).exists()}")
    return user.groups.filter(name='admin').exists()

# Shutdown System
@login_required
@user_passes_test(is_admin_user)
@csrf_exempt
def shutdown_system(request):
    if request.method == "POST":
        try:
            sudo = 'sudo' if os.geteuid() != 0 else ''
            # check if the user is pi or root
            result = subprocess.run(['chmod', '+x', './scripts/shutdown.sh'])
            if result.returncode != 0:
                raise Exception(f"Reboot script returned code{result.returncode}: {result}")     
            result =  subprocess.run([sudo, './scripts/shutdown.sh'])
            if result.returncode != 0:
                raise Exception(f"Reboot script returned code{result.returncode}: {result}") 

                    
            return JsonResponse({"message": "System is shutting down..."}, status=200)
        except Exception as e:
            return JsonResponse({"message": f"Error: {str(e)}"}, status=500)
    return JsonResponse({"message": "Invalid request method."}, status=405)

# Reboot System
@login_required
@user_passes_test(is_admin_user)
@csrf_exempt
def reboot_system(request):
    if request.method == "POST":
        try: 
            sudo = 'sudo' if os.geteuid() != 0 else ''
            # check if the user is pi or root
            result = subprocess.run(['chmod', '+x', './scripts/reboot.sh'])
            if result.returncode != 0:
                raise Exception(f"Reboot script returned code{result.returncode}: {result}")     
            result =  subprocess.run([sudo, './scripts/reboot.sh'])
            if result.returncode != 0:
                raise Exception(f"Reboot script returned code{result.returncode}: {result}") 
            return JsonResponse({"message": "System is rebooting..."}, status=200)
        except Exception as e:
            print(e)
            traceback.print_exc()
            return JsonResponse({"message": f"Error: {str(e)}"}, status=500)
    return JsonResponse({"message": "Invalid request method."}, status=405)
