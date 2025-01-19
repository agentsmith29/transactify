from django.urls import re_path
from .consumers.ScannerConsumer import PageSpecificConsumer
from .consumers.OLEDViewConsumer import OledDisplayConsumer
from .consumers.TerminalConsumer import TerminalConsumer
import os
from django.conf import settings

# Dynamically include the app name from settings.APPNAME
from config import CONFIG
import logging

websocket_urlpatterns = [
    re_path(f'^{CONFIG.webservice.SERVICE_NAME}' + r'/ws/page/(?P<page_name>\w+)/$', PageSpecificConsumer.as_asgi()),
    re_path(f'^{CONFIG.webservice.SERVICE_NAME}' + r'/ws/oled/$', OledDisplayConsumer.as_asgi()),
    re_path(f'^{CONFIG.webservice.SERVICE_NAME}' + r'/ws/register_store', TerminalConsumer.as_asgi()),
]

