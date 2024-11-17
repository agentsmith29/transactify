import asyncio

from server.TCPServer import TCPServer
from mfrc522 import MFRC522, SimpleMFRC522
from controller.KeyPad import KeyPad
import jsonpickle
import hashlib
class MainController():

    def __init__(self, rfid_reader: SimpleMFRC522, keypad: KeyPad):
        self.reader = rfid_reader
        self.keypad = keypad
    
        self.server = TCPServer(
            on_new_connection=self.on_new_connection,
            on_message_received=self.on_message_received
        )
        asyncio.run(self.server.start_server())

    async def on_new_connection(self, client_info):
        #await self.server.acknowledge()
        print(f"New connection from {client_info}")    
        await self.server.send_message("Welcome anonymous client. This is a secret interface!")
        #await self.server.acknowledge()

    async def on_message_received(self, client_info: str, message: str):
        await self.server.acknowledge()
        print(f"Received message from {client_info}: {message}")

        if message.lower() == "issue":
            await self.issue_new_card()

    async def issue_new_card(self):
        card_name = None
        deposit_amount = None
        await self.server.send_message("Issue a new card. Please enter the name of the card holder.")
        # wait for the response
        async def set_card_name(client, name, *args, **kwargs):
            print(f"Card name: {name}. args: {args}. kwargs: {kwargs}")
            await self.server.send_message(f"Name of the card holder has been set to: {name}. Please enter the amount to deposit.")
            card_name = name
            self.server._on_message_received = deposit
        print("I'll set the card name")
        self.server._on_message_received = set_card_name

        async def deposit(client, deposit, *args, **kwargs):
            print(f"Card name: {card_name} charged with {deposit} args: {args}. kwargs: {kwargs}")
            await self.server.send_message(f"Charged with {deposit}. Please present the card to the reader.")
            deposit_amount = deposit

            await self.reader.write(deposit_amount)
         


        self.server._on_message_received = self.on_message_received


    def construct_rfid_content(self, issuer, issued_on, surname, name, last_purchase="", last_updated="", balance = 0, purchases = 0):
        if last_updated == "" or last_updated is None:
            last_updated = issued_on

        content = {
            "issuer": issuer,
            "issued_on": issued_on,
            "card_holder_sname": surname,
            "card_name": name,
            "balance": balance,
            "purchases": balance,
            "last_purchase": last_purchase,
            "last_updated": last_updated,
        }
        # serialize the content
        serialized_dct = jsonpickle.encode(content)
        check_sum = hashlib.sha256(serialized_dct.encode('utf-8')).digest()
        print(serialized_dct)
        print(check_sum)

        # create a string from it

        
        



        # reset the on_message_received

        #await self.server.send_command("issue_cmd")