import asyncio
import aioconsole
from asyncio.streams import StreamReader

class TCPClient:
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port

        self._server_acknowleged = False

    async def send_message(self, writer):
            while True:
                if self._server_acknowleged:
                    message = await aioconsole.ainput('> ')
                    writer.write(message.encode())
                    await writer.drain()
                    if message.lower() == 'exit':
                        writer.close()
                        await writer.wait_closed()
                        break
                await asyncio.sleep(0.1)

    async def receive_message(self, reader: StreamReader):
        try:
            while True:
                data = await reader.read(2)
                cmd = data[0]
                cmd_len = data[1]
                if cmd_len > 0:
                     data = await reader.read(cmd_len)
                else:
                     data = None
                #if data is None or len(data) == 0:
                #    break
                #print(f"Recieved Data: {data}. CMD: {cmd}. LEN: {cmd_len}")
                #if not d:
                #    print("Server closed the connection.")
                #    break
                if cmd == 0xFF:
                    #print("ack") 
                    self._server_acknowleged = True
                elif cmd == 0xFE:
                    print(f"[SERVER]: {data.decode()}")
                #else:     
                #    print(f"[UNKNWM]: {data} / {str(0xFF)}")
        except asyncio.CancelledError:
                print("Receive task cancelled.")

    async def start_client(self):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        print(f"Connected to server at {self.host}:{self.port}")

        receive_task = asyncio.create_task(self.receive_message(reader))
        send_task = asyncio.create_task(self.send_message(writer))
        
        #await asyncio.gather(receive_message(), send_message())
        
        #receive_task.cancel()
        await send_task
        await receive_task

if __name__ == "__main__":
    # To run the server
    # server = TCPServer()
    # asyncio.run(server.start_server())

    # To run the client
    client = TCPClient()
    asyncio.run(client.start_client())
