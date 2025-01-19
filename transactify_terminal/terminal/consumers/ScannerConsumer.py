import json
from terminal.consumers.BaseConsumer import BaseAsyncWebsocketConsumer
from terminal.consumers.BaseConsumer import WebsocketSignals

class PageSpecificConsumer(BaseAsyncWebsocketConsumer):
    async def connect(self):
        # Define a group name based on the page
        self.page_name = self.scope['url_route']['kwargs']['page_name']
        self.group_name = f"page_{self.page_name}"

        # Add the WebSocket connection to the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the WebSocket connection from the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        self.logger.info(f"WebSocket  {self.scope['path']} disconnected: {self.scope['client']}")

    async def receive(self, text_data):
        # Handle incoming messages and broadcast to the group
        self.logger.debug(f"{self.scope['path']}: Received {text_data}.")
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'page_message',
                'message': text_data.strip(),
            }
        )

    async def page_message(self, event):
        # Send all fields (message and barcode) to the client
        # convert all fields to JSON
        asdict = dict(event)
        asjason = json.dumps(asdict)
        await self.send(text_data=asjason)
        self.logger.debug(f"{self.scope['path']}: Sent {asjason}.")