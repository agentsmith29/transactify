import json
import uuid
from asgiref.sync import sync_to_async

from django.utils import timezone

from terminal.consumers.BaseConsumer import BaseAsyncWebsocketConsumer
from terminal.consumers.BaseConsumer import WebsocketSignals




class TerminalConsumer(BaseAsyncWebsocketConsumer):
    signals = WebsocketSignals()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def connect(self):
        """
        Handle a new WebSocket connection.
        """
        self.uid = str(uuid.uuid4())  # Generate a unique connection UID
        await self.accept()

        # Reset all connections on server restart
        await self.reset_all_connections()

        # Register the new connection
        client_ip, client_port = self.scope["client"]
        await self.register_connection(self.uid, client_ip, client_port)

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        """
        self.logger.info(f"WebSocket connection closed. UID: {self.uid}")
        await self.set_connection_inactive(self.uid)

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages.
        """
        try:
            data = json.loads(text_data)
            self.logger.debug(f"Received data: {data}")
            name = data.get("name")
            address = data.get("address")
            docker_container = data.get("docker_container")
            terminal_button = data.get("terminal_button")
            await self.register_store(docker_container, name, address, docker_container, terminal_button)

            response = {"status": "success", "message": "Message received."}
            await self.send(text_data=json.dumps(response))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"status": "error", "message": "Invalid JSON"}))

    # --- Connection Utilities ---

    @sync_to_async
    def register_store(self, service_name, name, address, docker_container, terminal_button):
        """
        Register a new store in the database.
        """
        from terminal.webmodels import Store
        from terminal.webmodels import StoreConnection

        # check if the store is already registered
        if Store.objects.filter(service_name=service_name).exists():
            store = Store.objects.get(service_name=service_name)
            self.logger.warning(f"Store {store.name} ({store.service_name}) already registered.")
            store.name = name
            store.web_address = address
            store.docker_container = docker_container
            store.terminal_button = terminal_button
            store.is_connected = True
            store.save()
        else:
            # Register the store
            store, created = Store.objects.update_or_create(
                service_name=service_name,
                name=name,
                web_address=address,
                docker_container=docker_container,
                terminal_button=terminal_button,
                is_connected=True,
            )
        store_connection = StoreConnection.objects.get(uid=self.uid)
        store_connection.store = store
        store_connection.save()

        # Emit a signal for the new store
        self.signals.on_connect.send(sender=self, store=store)
        self.logger.info(f"Store {store.name} ({store.service_name}) registered.")


    @sync_to_async
    def register_connection(self, uid, ip, port):
        """
        Register a new WebSocket connection in the database.
        """
        from terminal.webmodels import Store, StoreConnection

        # Register the connection
        StoreConnection.objects.update_or_create(
            uid=uid,
            defaults={
                "store": None,
                "is_active": True,
                "ip_address": ip,
                "port": port,
            },
        )

        # Emit a signal for the new connection

    @sync_to_async
    def set_connection_inactive(self, uid):
        """
        Mark a WebSocket connection as inactive.
        """
        from terminal.webmodels import StoreConnection
        from terminal.webmodels import Store

        try:
            connection = StoreConnection.objects.get(uid=uid)
            # get all associated stors and set the connection to inactive

            connection.store.is_connected = False
            connection.store.save()    

            connection.is_active = False
            connection.disconnected_at = timezone.now()
            connection.save()

            # Emit a disconnect signal
            self.signals.on_disconnect.send(sender=self, connection=connection)
            self.logger.warning(f"Connection {uid} marked as inactive.")
        except StoreConnection.DoesNotExist:
            self.logger.warning(f"Connection {uid} not found.")

    @sync_to_async
    def reset_all_connections(self):
        """
        Reset all connections to inactive on server restart.
        """
        from terminal.webmodels import Store, StoreConnection

        StoreConnection.objects.filter(is_active=True).update(is_active=False, disconnected_at=timezone.now())
        Store.objects.filter(is_connected=True).update(is_connected=False)
        self.logger.warning("All connections reset on server restart.")
