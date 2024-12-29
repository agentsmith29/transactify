from django.dispatch import Signal

from ..ConfParser import Store

from .OLEDPage import OLEDPage
import os

from ...api_endpoints.StoreProduct import StoreProduct
from ...api_endpoints.Customer import Customer
import requests

import time
from random import randint
from luma.core.render import canvas
from random import randint, gauss
from luma.core.render import canvas
from luma.core.sprite_system import framerate_regulator

import asyncio

class OLEDScreenSaver(OLEDPage):
    name: str = "OLEDScreenSaver"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        OLEDScreenSaver.name: str = str(self.__class__.__name__) 

    def view(self, *args, **kwargs):
        self.screensaver_matrix()

    def on_btn_pressed(self, sender, kypd_btn, **kwargs):          
        if kypd_btn == 'D':
            self.view_controller.request_view(self.view_controller.PAGE_STORE_SELECTION)
            
        #self.display_message_overlay("Scan NFC to select store")
    
    # =================================================================================================================
    # Screensaver
    # =================================================================================================================
    def screensaver_game_of_life(self):
        def neighbors(cell):
            x, y = cell
            yield x - 1, y - 1
            yield x, y - 1
            yield x + 1, y - 1
            yield x - 1, y
            yield x + 1, y
            yield x - 1, y + 1
            yield x, y + 1
            yield x + 1, y + 1

        def iterate(board):
            new_board = set([])
            candidates = board.union(set(n for cell in board for n in neighbors(cell)))
            for cell in candidates:
                count = sum((n in board) for n in neighbors(cell))
                if count == 3 or (count == 2 and cell in board):
                    new_board.add(cell)
            return new_board
        
        def main():
            text = "Game of Life"
            scale = 3
            cols = self.view_controller.oled.width // scale
            rows = self.view_controller.oled.height // scale
            initial_population = int(cols * rows * 0.33)

            while not self.break_loop:
                board = set((randint(0, cols), randint(0, rows)) for _ in range(initial_population))

                for i in range(500):
                    with canvas(self.view_controller.oled, dither=True) as draw:
                        for x, y in board:
                            left = x * scale
                            top = y * scale
                            if scale == 1:
                                draw.point((left, top), fill="white")
                            else:
                                right = left + scale
                                bottom = top + scale
                                draw.rectangle((left, top, right, bottom), fill="white", outline="black")

                        if i == 0:
                            left, top, right, bottom = draw.textbbox((0, 0), text)
                            w, h = right - left, bottom - top

                            left = (self.view_controller.oled.width - w) // 2
                            top = (self.view_controller.oled.height - h) // 2
                            draw.rectangle((left - 1, top, left + w + 1, top + h), fill="black", outline="white")
                            draw.text((left + 1, top), text=text, fill="white")

                    if i == 0:
                        time.sleep(3)

                    board = iterate(board)
        
        main()

    def screensaver_matrix(self):
        device = self.view_controller.oled
        wrd_rgb = [
                (154, 173, 154),
                (0, 255, 0),
                (0, 235, 0),
                (0, 220, 0),
                (0, 185, 0),
                (0, 165, 0),
                (0, 128, 0),
                (0, 0, 0),
                (154, 173, 154),
                (0, 145, 0),
                (0, 125, 0),
                (0, 100, 0),
                (0, 80, 0),
                (0, 60, 0),
                (0, 40, 0),
                (0, 0, 0)
            ]

        clock = 0
        blue_pilled_population = []
        max_population = device.width * 8
        regulator = framerate_regulator(fps=10)

        def increase_population():
            blue_pilled_population.append([randint(0, device.width), 0, gauss(1.2, 0.6)])

        while not self.break_loop:
            clock += 1
            with regulator:
                with canvas(device, dither=True) as draw:
                    for person in blue_pilled_population:
                        x, y, speed = person
                        for rgb in wrd_rgb:
                            if 0 <= y < device.height:
                                draw.point((x, y), fill=rgb)
                            y -= 1
                        person[1] += speed

            if clock % 5 == 0 or clock % 3 == 0:
                increase_population()

            while len(blue_pilled_population) > max_population:
                blue_pilled_population.pop(0)


    def on_nfc_read(self, sender, id, text, **kwargs):
        #customer_entries = [self._fetch_customer(self.view_controller, store, card_number=id) for store in self.stores if not None]
        customer_entries = []
        for store in self.stores:
            customer = self._fetch_customer(self.view_controller, store, card_number=id)
            if customer is not None:
                customer_entries.append(customer)

        print(f"Customer entries: {customer_entries}")
        if len(customer_entries) == 0:
            self.view_controller.request_view(self.view_controller.PAGE_CUSTOMER_UNKNW,
                                             id=id,
                                             # Next view handler
                                            next_view=self.view_controller.PAGE_STORE_SELECTION)
        elif len(customer_entries) == 1:
            self.view_controller.request_view(self.view_controller.PAGE_CUSTOMER, 
                                              store=customer_entries[0].store, 
                                              customer=customer_entries[0],
                                              # Next view handler
                                              next_view=self.view_controller.PAGE_STORE_SELECTION)
        
        elif len(customer_entries) > 1:
            self.display_message_overlay("Multiple store entries. Please use select the store to display the balance.")


    def on_barcode_read(self, sender, barcode, **kwargs):
        self._on_barcode_read_request_products_view(view_controller=self.view_controller, 
                                               stores=self.stores,
                                               barcode=barcode) 
    

    def __del__(self):
        return super().__del__()