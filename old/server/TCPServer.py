import asyncio
from asyncio.streams import StreamWriter

class TCPMessage():
    def __init__(self, msg):
        self.message = msg
    
class TCPServer:
    def __init__(self, host='127.0.0.1', port=8888,
                 on_new_connection: callable = None, on_message_received: callable = None):
        self.host = host
        self.port = port
        self.clients = []

        self._on_new_connection = on_new_connection
        self._on_message_received = on_message_received

    async def handle_client(self, reader, writer):
        client_info = writer.get_extra_info('peername')
        #print(f"New connection from {client_info}")
        self.clients.append(writer)  
        if self._on_new_connection is not None:
            await self._on_new_connection(client_info)

        try:
            print(f"Starting talking to {self.clients}")
            while True:
                data = await reader.read(255)
                if not data:
                    print(f"Connection closed by {client_info}")
                    break
                message = data.decode()
                #print(f"Received message from {client_info}: {message}")
                if self._on_new_connection is not None:
                    await self._on_message_received(client_info, message)
                
                # Echo back to all clients
                #for client_writer in self.clients:
                #    if client_writer != writer:
                #        client_writer.write(data)
                #        await client_writer.drain()


        except asyncio.CancelledError:
            print("Client handler task was cancelled.")
        finally:
            self.clients.remove(writer)
            writer.close()
            await writer.wait_closed()
            print(f"Closed connection to {client_info}")

    async def acknowledge(self, client=None):
       print("Sending acknowledge byte")
       await self._send(client, self.construct_command('', 0xFF))
                
    async def send_command(self, cmd, client=None):
       #await self._send(client, str(0xFE)
       await self._send(client, f"cmd: {cmd}\n".encode())
    
    def construct_command(self, data, code):
        data_len = len(data)  # the length of the message, represented as an 8-bit value
        # Combine them by shifting msg_code to the left by 8 bits and adding msg_len
        ack_byte = (code << 8) | data_len
        # construct a byte where the first byte is xFE and the second byte is the length of the message
        final_msg = ack_byte.to_bytes(2, byteorder='big') + data.encode()
        return final_msg

    async def send_message(self, msg, client=None):
        await self._send(client, self.construct_command(msg, 0xFE))
        await self.acknowledge(client)

    async def _send(self, client, data):
        for client_writer in list(self.clients):  # Copy the list to avoid modification during iteration
                client_writer: StreamWriter
                try:
                    client_writer.write(data)
                    await client_writer.drain()
                    # flush
                    print("Written!")
                except Exception as e:
                    print(f"Failed to send message to {client_writer.get_extra_info('peername')}: {e}")
                    self.clients.remove(client_writer)  # Remove any clients with failed connections



    async def broadcast_message(self, message, exclude=None):
        """
        Broadcast a message to all clients except the excluded one.
        """
        
        for client_writer in list(self.clients):  # Copy the list to avoid modification during iteration
            print(f"Starting broadcast to {client_writer}")
            if exclude is not None or client_writer != exclude:
                try:
                    client_writer.write(message.encode())
                    await client_writer.drain()
                    print(f"Sent broadcast to {client_writer.get_extra_info('peername')}")
                except Exception as e:
                    print(f"Failed to send message to {client_writer.get_extra_info('peername')}: {e}")
                    self.clients.remove(client_writer)  # Remove any clients with failed connections
            else:
                print("Excluded..!")

    async def start_server(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        async with server:
            print(f"Server started on {self.host}:{self.port}")
            await server.serve_forever()


if __name__ == "__main__":
    pass
    # To run the server
    # server = TCPServer()
    # asyncio.run(server.start_server())

    # To run the client
    # client = TCPClient()
    # asyncio.run(client.start_client())
