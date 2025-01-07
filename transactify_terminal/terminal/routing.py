from django.urls import re_path
from .consumers.ScannerConsumer import PageSpecificConsumer
from .consumers.OLEDViewConsumer import OledDisplayConsumer
import os
# Dynamically include the app name from settings.APPNAME
app_prefix = os.getenv('SERVICE_NAME')

websocket_urlpatterns = [
    re_path(f'^{app_prefix}' + r'/ws/page/(?P<page_name>\w+)/$', PageSpecificConsumer.as_asgi()),
    re_path(f'^{app_prefix}' + r'/ws/oled/$', OledDisplayConsumer.as_asgi()),
]
#websocket_urlpatterns = [
#    re_path(r'^ws/page/(?P<page_name>\w+)/$', PageSpecificConsumer.as_asgi()),
#    re_path(r'^ws/oled/$', OledDisplayConsumer.as_asgi()),
#]

print(f"Websocket URL patterns: {websocket_urlpatterns}")