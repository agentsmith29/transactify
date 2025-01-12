import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TerminalConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("WebSocket connection established")

    async def disconnect(self, close_code):
        print(f"WebSocket connection closed with code {close_code}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            print(f"Received data from store: {data}")

            # Process the incoming data (store config)
            store_name = data.get("name", "Unknown")
            store_address = data.get("address", "Unknown")
            print(f"Store Name: {store_name}, Address: {store_address}")

            # Respond back to the client
            response = {
                "status": "success",
                "message": f"Received config for store: {store_name}"
            }
            await self.send(text_data=json.dumps(response))

        except json.JSONDecodeError as e:
            print(f"Invalid JSON received: {text_data}")
            await self.send(text_data=json.dumps({"status": "error", "message": "Invalid JSON"}))
