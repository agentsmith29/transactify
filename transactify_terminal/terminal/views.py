from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views import View
import json
from .webmodels import Store


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

def register_store(request):
    config = request.POST.get('config')
    name = config['name']
    address = config['address']
    docker_container = config['docker_container']
    terminal_button = config['terminal_button']

    # Create or update the store
    store, created = Store.objects.update_or_create(
        service_name=name,
        name=name,
        defaults={'address': address, 'docker_container': docker_container, 'terminal_button': terminal_button}
    )
    print(f"I registered a store: {store}")