from django.urls import re_path, path
from store.ScannerComsumer import PageSpecificConsumer

websocket_urlpatterns = [
    re_path(r'^ws/page/(?P<page_name>\w+)/$', PageSpecificConsumer.as_asgi()),

]
