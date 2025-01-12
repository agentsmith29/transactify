from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
import json

from .apps import hwcontroller

#@csrf_exempt
class API_ReadNFCBlocking(View):

    def get(self, request):
        id, txt = hwcontroller.hwif.nfc_reader.read_block()
        # return a correct response
        return JsonResponse({'id': id, 'content': txt})

    def post(self, request):
        pass
    