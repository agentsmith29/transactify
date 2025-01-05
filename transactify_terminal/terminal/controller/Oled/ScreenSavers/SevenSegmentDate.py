#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-2022 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Example for seven segment displays.
"""

import sys
import time
from datetime import datetime

from luma.core.virtual import viewport, sevensegment

class SevenSegmentDate:
    def __init__(self, device, break_loop):
        self.device = device
        self.break_loop = break_loop
    
    def date(self, seg):
        """
        Display current date on device.
        """
        now = datetime.now()
        seg.text = now.strftime("%y-%m-%d")


    def clock(self, seg, seconds):
        """
        Display current time on self.device.
        """
        interval = 0.5
        for i in range(int(seconds / interval)):
            now = datetime.now()
            seg.text = now.strftime("%H-%M-%S")

            # calculate blinking dot
            if i % 2 == 0:
                seg.text = now.strftime("%H-%M-%S")
            else:
                seg.text = now.strftime("%H %M %S")

            time.sleep(interval)


    def show_message_vp(self, msg, delay=0.1):
        # Implemented with virtual viewport
        width = self.device.width
        padding = " " * width
        msg = padding + msg + padding
        n = len(msg)

        virtual = viewport(self.device, width=n, height=8)
        sevensegment(virtual).text = msg
        for i in reversed(list(range(n - width))):
            virtual.set_position((i, 0))
            time.sleep(delay)


    def show_message_alt(self, seg, msg, delay=0.1):
        # Does same as above but does string slicing itself
        width = seg.device.width
        padding = " " * width
        msg = padding + msg + padding

        for i in range(len(msg)):
            seg.text = msg[i:i + width]
            time.sleep(delay)


    def main(self):
        if not hasattr(self.device, 'segment_mapper'):
            sys.exit(f'sevensegment is not supported on a {self.device.__class__.__name__} self.device')

        seg = sevensegment(self.device)

        print('Simple text...')
        for _ in range(8):
            seg.text = "HELLO"
            time.sleep(0.6)
            seg.text = " GOODBYE"
            time.sleep(0.6)

        # Digit slicing
        print("Digit slicing")
        seg.text = "_" * seg.device.width
        time.sleep(1.0)

        for i, ch in enumerate([9, 8, 7, 6, 5, 4, 3, 2]):
            seg.text[i] = str(ch)
            time.sleep(0.6)

        for i in range(len(seg.text)):
            del seg.text[0]
            time.sleep(0.6)

        # Scrolling Alphabet Text
        print('Scrolling alphabet text...')
        self.show_message_vp(self.device, "HELLO EVERYONE!")
        self.show_message_vp(self.device, "PI is 3.14159 ... ")
        self.show_message_vp(self.device, "IP is 127.0.0.1 ... ")
        self.show_message_alt(seg, "0123456789 abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ")

        # Digit futzing
        self.date(seg)
        time.sleep(5)
        self.clock(seg, seconds=10)

        # Brightness
        print('Brightness...')
        for x in range(5):
            for intensity in range(16):
                seg.device.contrast(intensity * 16)
                time.sleep(0.1)
        self.device.contrast(0x7F)