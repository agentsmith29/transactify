import json
import uuid
from asgiref.sync import sync_to_async

from django.utils import timezone

from terminal.consumers.BaseConsumer import BaseAsyncWebsocketConsumer
from terminal.consumers.BaseConsumer import WebsocketSignals

from django.utils.timezone import now, timedelta


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

        ## Reset all connections on server restart
        #await self.reset_all_connections()

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
            cmd = data.get("cmd")
            if cmd == "register_store":
                await self.cmd_register_store(data)
            elif cmd == "echo":
                await self.cmd_echo(data)
            else:
                await self.cmd_received(data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"status": "error", "message": "Invalid JSON"}))

    async def cmd_echo(self, data):
        """
        Echo the received message back to the client.
        """
        params = data.get("params")
        message = params.get("message")
        response = {"status": "success", "message": f"You sent: {message}", 'cmd': 'echo'}
        await self.send(text_data=json.dumps(response))

    async def cmd_register_store(self, data):
        try:
            params = data.get("params")
            name = params.get("name")
            address = params.get("address")
            docker_container = params.get("docker_container")
            terminal_button = params.get("terminal_button")
            await self.register_store(docker_container, name, address, docker_container, terminal_button)

            response = {"status": "success", "message": "Store registered", 'cmd': 'register_store'}
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
            if connection.store:
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

    # --- view utilities ---
    @sync_to_async
    def cmd_received(self, cmd):
        """
        Request the current view from the terminal.
        """
        self.signals.on_cmd_received.send(sender=self, cmd=cmd)
import asyncio


























# class TerminalConsumer(BaseAsyncWebsocketConsumer):
#     signals = WebsocketSignals()

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     async def connect(self):
#         """
#         Handle a new WebSocket connection.
#         """
#         self.uid = str(uuid.uuid4())  # Generate a unique connection UID
#         await self.accept()

#         # Periodically check for stale connections
#         self.check_task = asyncio.create_task(self.periodically_check_connections())

#         # Reset all connections on server restart
#         # await self.reset_all_connections()

#         # Register the new connection
#         client_ip, client_port = self.scope["client"]
#         await self.register_connection(self.uid, client_ip, client_port)
    
#     async def periodically_check_connections(self):
#         """
#         Periodically call check_stale_connections to mark stale connections as inactive.
#         """
#         while True:
#             await asyncio.sleep(300)  # Check every 5 minutes
#             await sync_to_async(check_stale_connections)()

#     async def disconnect(self, close_code):
#         """
#         Handle WebSocket disconnection.
#         """
#         self.logger.info(f"WebSocket connection closed. UID: {self.uid}")
#         await self.set_connection_inactive(self.uid)
#         self.logger.info(f"Connection {self.uid} marked as inactive.")

#     async def receive(self, text_data):
#         """
#         Handle incoming WebSocket messages.
#         """
#         try:
#             data = json.loads(text_data)
#             self.logger.debug(f"Received data: {data}")
#             cmd = data.get("cmd")
#             if cmd == "register_store":
#                 await self.cmd_register_store(data)
#             elif cmd == "echo":
#                 await self.cmd_echo(data)
#             else:
#                 await self.cmd_received(data)
#         except json.JSONDecodeError:
#             await self.send(text_data=json.dumps({"status": "error", "message": "Invalid JSON"}))

#     async def cmd_echo(self, data):
#         """
#         Echo the received message back to the client.
#         """
#         params = data.get("params")
#         message = params.get("message")
#         response = {"status": "success", "message": f"You sent: {message}", 'cmd': 'echo'}
#         await self.send(text_data=json.dumps(response))

#     async def cmd_register_store(self, data):
#         try:
#             params = data.get("params")
#             name = params.get("name")
#             address = params.get("address")
#             docker_container = params.get("docker_container")
#             terminal_button = params.get("terminal_button")
#             await self.register_store(docker_container, name, address, docker_container, terminal_button)

#             response = {"status": "success", "message": "Store registered", 'cmd': 'register_store'}
#             await self.send(text_data=json.dumps(response))
#         except json.JSONDecodeError:
#             await self.send(text_data=json.dumps({"status": "error", "message": "Invalid JSON"}))

#     # --- Connection Utilities ---

#     @sync_to_async
#     def register_store(self, service_name, name, address, docker_container, terminal_button):
#         """
#         Register a new store in the database.
#         """
#         from terminal.webmodels import Store
#         from terminal.webmodels import StoreConnection

#         # check if the store is already registered
#         if Store.objects.filter(service_name=service_name).exists():
#             store = Store.objects.get(service_name=service_name)
#             self.logger.warning(f"Store {store.name} ({store.service_name}) already registered.")
#             store.name = name
#             store.web_address = address
#             store.docker_container = docker_container
#             store.terminal_button = terminal_button
#             store.is_connected = True
#             store.save()
#         else:
#             # Register the store
#             store, created = Store.objects.update_or_create(
#                 service_name=service_name,
#                 name=name,
#                 web_address=address,
#                 docker_container=docker_container,
#                 terminal_button=terminal_button,
#                 is_connected=True,
#             )
#         store_connection = StoreConnection.objects.get(uid=self.uid)
#         store_connection.store = store
#         store_connection.save()

#         # Emit a signal for the new store
#         self.signals.on_connect.send(sender=self, store=store)
#         self.logger.info(f"Store {store.name} ({store.service_name}) registered.")

#     @sync_to_async
#     def register_connection(self, uid, ip, port):
#         """
#         Register a new WebSocket connection in the database.
#         """
#         from terminal.webmodels import Store, StoreConnection

#         # Register the connection
#         StoreConnection.objects.update_or_create(
#             uid=uid,
#             defaults={
#                 "store": None,
#                 "is_active": True,
#                 "ip_address": ip,
#                 "port": port,
#             },
#         )

#         # Emit a signal for the new connection

#     @sync_to_async
#     def set_connection_inactive(self, uid):
#         """
#         Mark a WebSocket connection as inactive and update the store's status if no active connections remain.
#         """
#         from terminal.webmodels import StoreConnection

#         try:
#             connection = StoreConnection.objects.get(uid=uid)
#             if connection.store:
#                 # Check if there are other active connections for the same store
#                 active_connections = StoreConnection.objects.filter(store=connection.store, is_active=True).exclude(uid=uid)
#                 if not active_connections.exists():
#                     connection.store.is_connected = False
#                     connection.store.save()

#             connection.is_active = False
#             connection.disconnected_at = timezone.now()
#             connection.save()
#             self.logger.warning(f"Connection {uid} marked as inactive.")
#             self.signals.on_disconnect.send(sender=self, connection=connection)
#         except StoreConnection.DoesNotExist:
#             self.logger.warning(f"Connection {uid} not found.")

#     @sync_to_async
#     def reset_all_connections(self):
#         """
#         Reset all connections to inactive on server restart. Skip if already handled.
#         """
#         from terminal.webmodels import StoreConnection

#         # Mark all connections inactive and reset stores
#         StoreConnection.objects.filter(is_active=True).update(is_active=False, disconnected_at=timezone.now())
#         self.logger.warning("All connections reset on server restart.")

#     from django.utils.timezone import now, timedelta

    

#     # --- view utilities ---
#     @sync_to_async
#     def cmd_received(self, cmd):
#         """
#         Request the current view from the terminal.
#         """
#         self.signals.on_cmd_received.send(sender=self, cmd=cmd)


# @sync_to_async
# def check_stale_connections():
#     """
#     Periodically check for stale WebSocket connections and mark them as inactive.
#     """
#     from terminal.webmodels import StoreConnection

#     timeout_threshold = now() - timedelta(minutes=5)  # Consider connections inactive if no activity for 5 minutes
#     stale_connections = StoreConnection.objects.filter(is_active=True, last_activity__lt=timeout_threshold)
#     for connection in stale_connections:
#         connection.is_active = False
#         connection.disconnected_at = now()
#         connection.save()
#         connection.store.is_connected = False
#         connection.store.save()
#         #self.logger.warning(f"Stale connection {connection.uid} marked as inactive.")