import json
from channels.generic.websocket import AsyncWebsocketConsumer

class OledDisplayConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the WebSocket connection
        await self.channel_layer.group_add("oled_display", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
         await self.channel_layer.group_discard("oled_display", self.channel_name)

    async def receive(self, text_data):
        # Echo messages (useful for debugging, optional)
        data = json.loads(text_data)
        await self.send(text_data=json.dumps(data))

    async def display_image(self, event):
        # Send the OLED image data to the WebSocket client
        image_data = event['image_data']
        await self.send(text_data=json.dumps({'image_data': image_data}))
        #print(f"Image data sent to OLED display: {image_data}")
