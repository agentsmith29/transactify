import os
from terminal.routing import websocket_urlpatterns
import logging
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "transactify_terminal.settings")

# Configure logging

class LoggingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Log the incoming request scope
        print(f"ASGI Scope: {scope}")
        
        # Log specific WebSocket events
        if scope["type"] == "websocket":
            print(f"WebSocket connection: {scope['client']} {scope['path']}")
        
        # Continue processing the request
        inner = self.app(scope)
        return await inner(receive, send)

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        #LoggingMiddleware(
            URLRouter(websocket_urlpatterns)
        #)
    ),
})
