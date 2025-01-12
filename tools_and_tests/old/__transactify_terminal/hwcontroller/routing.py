from django.urls import re_path
from .ScannerComsumer import PageSpecificConsumer

websocket_urlpatterns = [
    re_path(r'^tcon/page/(?P<page_name>\w+)/$', PageSpecificConsumer.as_asgi()),
]
