from channels.generic.websocket import AsyncWebsocketConsumer
import json

class PageSpecificConsumer(AsyncWebsocketConsumer):
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
        print(f"WebSocket connection established for page: {self.page_name}")

    async def disconnect(self, close_code):
        # Remove the WebSocket connection from the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        print(f"WebSocket disconnected from page: {self.page_name}")

    async def receive(self, text_data):
        # Handle incoming messages and broadcast to the group
        print(f"Received message: {text_data} for page: {self.page_name}")
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'page_message',
                'message': text_data.strip(),
            }
        )

    async def page_message(self, event):
        # Send all fields (message and barcode) to the client
        await self.send(text_data=json.dumps({
            "message": event.get("message"),
            "barcode": event.get("barcode"),
        }))
        print(f"Message broadcasted: {event}")