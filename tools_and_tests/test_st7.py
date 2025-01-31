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
from operator import itemgetter
from luma.core.render import canvas
from luma.core.sprite_system import framerate_regulator


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


if __name__ == "__main__":
    try:
        from luma.core.interface.serial import i2c, spi, pcf8574
        from luma.core.render import canvas
        from luma.lcd.device import ili9341 as dev1#, st7567, uc1701x, ili9341, ili9486, hd44780
        from luma.oled.device import ssd1322 as dev2	

        #serial1 = spi(port=0, device=0, gpio_DC=25, gpio_RST=12)
        #device = dev1(serial1, width=320, height=240, bgr=True )

        serial2 = spi(port=0, device=1, gpio_DC=23, gpio_RST=24)
        device = dev2(serial2, width=256, height=64, bgr=True )
        main()
        
        #with canvas(device) as draw:
        #    draw.rectangle(device.bounding_box, outline="white", fill="black")
        #    draw.text((30, 40), "Hello World", fill="red")
        #    # wait for key press
        #    input("Press any key...")
    except KeyboardInterrupt:
        pass