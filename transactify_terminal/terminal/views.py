from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views import View
import json
from .webmodels.Store  import Store


from .apps import hwcontroller

#@csrf_exempt
class API_ReadNFCBlocking(View):

    def get(self, request):
        id, txt = hwcontroller.hwif.nfc_reader.read_block()
        # return a correct response
        return JsonResponse({'id': id, 'content': txt})

    def post(self, request):
        pass
    

#@login_required
def oled_display(request):
    """
    View to render the OLED display HTML page.
    """
    return render(request, 'hwcontroller/view_oled.html', {'current_image': hwcontroller.view_controller.current_view.oled_image_base64})

