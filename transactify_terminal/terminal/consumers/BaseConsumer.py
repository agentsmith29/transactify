

from channels.generic.websocket import AsyncWebsocketConsumer
from django.dispatch import Signal
import logging
from transactify_terminal.settings import CONFIG

class WebsocketSignals:
    on_connect = Signal()
    on_disconnect = Signal()

class BaseAsyncWebsocketConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = WebsocketSignals()   
        self.logger = logging.getLogger(f"{CONFIG.webservice.SERVICE_NAME}.consumers.{self.__class__.__name__}")
    
    def accept(self, subprotocol=None, headers=None):
        self.logger.info(f"WebSocket connection established {self.scope['path']}: {self.scope['client']}")
        return super().accept(subprotocol, headers)