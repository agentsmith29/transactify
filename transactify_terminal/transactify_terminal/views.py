from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpResponse


def health_check(request):
    print(f'Health check request from {request.META.get("REMOTE_ADDR")}')
    # 200 response for health check
    return HttpResponse(status=200)