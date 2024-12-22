from django.urls import re_path
from .consumers.ScannerConsumer import PageSpecificConsumer
from .consumers.OLEDViewConsumer import OledDisplayConsumer

websocket_urlpatterns = [
    re_path(r'^tcon/page/(?P<page_name>\w+)/$', PageSpecificConsumer.as_asgi()),
    re_path(r'^tcon/oled/$', OledDisplayConsumer.as_asgi()),
]
