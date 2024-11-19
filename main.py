#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Rotating 3D box wireframe & color dithering.

Adapted from:
http://codentronix.com/2011/05/12/rotating-3d-cube-using-python-and-pygame/
"""

import sys
import math
from time import sleep

from operator import itemgetter
from demo_opts import get_device
from luma.core.render import canvas
from luma.core.sprite_system import framerate_regulator


from luma.core.interface.parallel import bitbang_6800
from luma.core.render import canvas


from server.TCPServer import TCPServer
from controller.MainController import MainController

from luma.core.interface.serial import spi
from luma.oled.device import ssd1322 as OLED
from controller.KeyPad import KeyPad 
from mfrc522.SimpleMFRC522 import SimpleMFRC522

import RPi.GPIO as GPIO



import asyncio


def radians(degrees):
    return degrees * math.pi / 180


class point(object):

    def __init__(self, x, y, z):
        self.coords = (x, y, z)
        self.xy = (x, y)
        self.z = z

    def rotate_x(self, angle):
        x, y, z = self.coords
        rad = radians(angle)
        c = math.cos(rad)
        s = math.sin(rad)
        return point(x, y * c - z * s, y * s + z * c)

    def rotate_y(self, angle):
        x, y, z = self.coords
        rad = radians(angle)
        c = math.cos(rad)
        s = math.sin(rad)
        return point(z * s + x * c, y, z * c - x * s)

    def rotate_z(self, angle):
        x, y, z = self.coords
        rad = radians(angle)
        c = math.cos(rad)
        s = math.sin(rad)
        return point(x * c - y * s, x * s + y * c, z)

    def project(self, size, fov, viewer_distance):
        x, y, z = self.coords
        factor = fov / (viewer_distance + z)
        return point(x * factor + size[0] / 2, -y * factor + size[1] / 2, z)


def sine_wave(min, max, step=1):
    angle = 0
    diff = max - min
    diff2 = diff / 2
    offset = min + diff2
    while True:
        yield angle, offset + math.sin(radians(angle)) * diff2
        angle += step


def main(num_iterations=sys.maxsize):

    regulator = framerate_regulator(fps=30)

    vertices = [
        point(-1, 1, -1),
        point(1, 1, -1),
        point(1, -1, -1),
        point(-1, -1, -1),
        point(-1, 1, 1),
        point(1, 1, 1),
        point(1, -1, 1),
        point(-1, -1, 1)
    ]

    faces = [
        ((0, 1, 2, 3), "red"),
        ((1, 5, 6, 2), "green"),
        ((0, 4, 5, 1), "blue"),
        ((5, 4, 7, 6), "magenta"),
        ((4, 0, 3, 7), "yellow"),
        ((3, 2, 6, 7), "cyan")
    ]

    a, b, c = 0, 0, 0

    for angle, dist in sine_wave(8, 40, 1.5):
        with regulator:
            num_iterations -= 1
            if num_iterations == 0:
                break

            t = [v.rotate_x(a).rotate_y(b).rotate_z(c).project(device.size, 256, dist)
                for v in vertices]

            depth = []
            for idx, face in enumerate(faces):
                v1, v2, v3, v4 = face[0]
                avg_z = (t[v1].z + t[v2].z + t[v3].z + t[v4].z) / 4.0
                depth.append((idx, avg_z))

            with canvas(device, dither=True) as draw:
                for idx, depth in sorted(depth, key=itemgetter(1), reverse=True)[3:]:
                    (v1, v2, v3, v4), color = faces[idx]

                    if angle // 720 % 2 == 0:
                        fill, outline = color, color
                    else:
                        fill, outline = "black", "white"

                    draw.polygon(t[v1].xy + t[v2].xy + t[v3].xy + t[v4].xy, fill, outline)

            a += 0.3
            b -= 1.1
            c += 0.85

class View():
    def __init__(self, display: ssd1322):
        self.display = display


    async def read_keypad_input(self):
        try:
            while True:
                btn_pressed = await self.keypad.read_keypad()
                if btn_pressed is not None:
                    self.on_keypad_pressed(btn_pressed)
        except KeyboardInterrupt:
            print("Exiting program")

    def on_keypad_pressed(self, key):
        pass

class DepositView(View):
    def __init__(self, display: ssd1322, rfid_reader: SimpleMFRC522, keypad: KeyPad):
        View.__init__(self, display, rfid_reader, keypad)
        
    def show(self):
        with canvas(self.display) as draw:
            draw.rectangle(self.display.bounding_box, outline="white", fill="black")
            draw.text((30, 40), "Deposit: Please present card, enter amount and press F.", fill="white")

        id, text =self.reader.read()



class MainView(View):
    
    def __init__(self, display: ssd1322):
        View.__init__(self, display, rfid_reader, keypad)

        with canvas(self.display) as draw:
            draw.rectangle(self.display.bounding_box, outline="white", fill="black")
            draw.text((30, 40), "Present card or input access code", fill="white")
    
    async def run(self):
        """
        Runs the read_keypad and update_display tasks concurrently.
        """
        #asyncio.run(self.read_keypad_input(self.keypad))
        await asyncio.gather(
            self.read_keypad_input(),
            #self.update_display(),
        )
        
    def on_keypad_pressed(self, key):
        if key == 'A':
            """Open View"""
            dv = DepositView(self.display, self.reader, self.keypad)
            dv.show()


    async def read_keypad_input(self):
        try:
            while True:
                btn_pressed = await self.keypad.read_keypad()
                if btn_pressed is not None:
                    if btn_pressed == 'A':
                        """Open View"""
                        dv = DepositView(self.display, self.reader, self.keypad)
                        dv.show()
                     #with canvas(self.display) as draw:
                     #   draw.rectangle(self.display.bounding_box, outline="white", fill="black")
                     #   draw.text((30, 40), btn_pressed, fill="white")
        except KeyboardInterrupt:
            print("Exiting program")

        finally:
            GPIO.cleanup()


if __name__ == "__main__":
    try:
        keypad = KeyPad()
        reader = SimpleMFRC522()
        controller = MainController(reader, keypad)
        #view = MainView()
        #serial_monitor = spi(port = 0, device=1, gpio_DC=23, gpio_RST=24)
        #display = ssd1322(serial_monitor)
        #reader = SimpleMFRC522()
        #keypad = KeyPad()

        #main_view = MainView(display, reader, keypad)
        #asyncio.run(main_view.run())
    except KeyboardInterrupt:
        print("Exiting program")

    finally:
        GPIO.cleanup()