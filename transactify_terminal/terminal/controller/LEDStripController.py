import RPi.GPIO as GPIO
import time
import threading
import asyncio

from django.dispatch import Signal

import logging


import time
from rpi_ws281x import PixelStrip, Color
import argparse
from transactify_terminal.settings import CONFIG

from .BaseHardware import BaseHardware

class LEDStripController(BaseHardware):

    def __init__(self):
        super().__init__()
        # LED strip configuration:
        self.LED_COUNT = 8        # Number of LED pixels.
        self.LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
        # LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
        self.LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
        self.LED_DMA = 10          # DMA channel to use for generating signal (try 10)
        self.LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
        self.LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
        self.LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
        try:
            # Create NeoPixel object with appropriate configuration.
            self.strip = PixelStrip(
                self.global_config.ledstrip.LED_COUNT, 
                self.global_config.ledstrip.LED_PIN, 
                self.global_config.ledstrip.LED_FREQ_HZ, 
                self.global_config.ledstrip.LED_DMA, 
                self.global_config.ledstrip.LED_INVERT, 
                self.global_config.ledstrip.LED_BRIGHTNESS, 
                self.global_config.ledstrip.LED_CHANNEL)   
            self.strip.begin()

            self.break_loop = False
            self.logger.info(f"LEDStripeController initialized with {self.LED_COUNT} LEDs on GPIO {self.LED_PIN}")
            self.animation_thread: threading.Thread = None
            self.animate(self._testing_animation)
        except Exception as e:
            self.logger.error(f"Error initializing LEDStripeController: {e}")
            return  
        self.is_initialized = True

    def _check_if_initialized(func):
        def wrapper(self, *args, **kwargs):
            if not self.is_initialized:
                self.logger.warning("LEDStripeController not initialized. Returning.")
                return
            return func(self, *args, **kwargs)
        return wrapper
    
    @_check_if_initialized
    def animate(self, animation_function: callable):
        try:
             # Check if a thread is already running, and if cancel it.
            self.stop_animation()

            self.break_loop = False
            # Intialize the library (must be called once before other functions).
            self.logger.debug("Starting animation thread.")
            self.animation_thread = threading.Thread(target=animation_function,  daemon=True)
            self.animation_thread.start()
            self.logger.debug("Animation thread started.")
        except Exception as e:
            self.logger.error(f"LED animation failed: {e}")
            return
        
    
    @_check_if_initialized
    def stop_animation(self):
        if not self.is_initialized:
            self.logger.warning("LEDStripeController not initialized. Returning.")
            return

        if self.animation_thread is not None:
            print("Stopping animation thread.")
            self.break_loop = True
            time.sleep(0.1)
            self.animation_thread.join()
            print("Animation thread stopped.")
        self.colorWipe(Color(0, 0, 0), 10)

    def _testing_animation(self):
        print("Testing animation.")
        try:
            while not self.break_loop:
                self.colorWipe(Color(255, 0, 0))  # Red wipe
                self.colorWipe(Color(0, 255, 0))  # Green wipe
                self.colorWipe(Color(0, 0, 255))  # Blue wipe
            print("Animation stopped.")

        except KeyboardInterrupt:
            self.colorWipe(Color(0, 0, 0), 10)
        
        except Exception as e:
            print(f"Error in LEDStripController: {e}")
            self.colorWipe(Color(0, 0, 0), 10)


    # Define functions which animate LEDs in various ways.
    def colorWipe(self, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    def pulse(self, color: Color, duration):
        """ 
         Generate a hearbeat pulse effect.
         duration is the duration of fading in and out

        """
        steps = 1
        max_steps = self.LED_BRIGHTNESS
        time_sleep = (duration / ( (max_steps/steps)*2) )
        
        time_start = time.time()
        for i in range(0, max_steps, steps):
            for j in range(self.strip.numPixels()):
                self.strip.setPixelColor(j, color)
                self.strip.setBrightness(int(i))
            if self.break_loop:
                return
            self.strip.show()
            time.sleep(time_sleep)
        for i in range(max_steps, 0, -steps):
            for j in range(self.strip.numPixels()):
                self.strip.setPixelColor(j, color)
                self.strip.setBrightness(int(i))
            if self.break_loop:
                return
            self.strip.show()
            time.sleep(time_sleep)
        time_end = time.time()
        # print(f"Pulse duration: {time_end - time_start}")


    def theaterChase(self, color, wait_ms=50, iterations=10):
        """Movie theater light style chaser animation."""
        for j in range(iterations):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, color)
                self.strip.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, 0)


    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)


    def rainbow(self, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        for j in range(256 * iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.wheel((i + j) & 255))
            self.strip.show()
            time.sleep(wait_ms / 1000.0)


    def rainbowCycle(self, wait_ms=20, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256 * iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.wheel(
                    (int(i * 256 / self.strip.numPixels()) + j) & 255))
            self.strip.show()
            time.sleep(wait_ms / 1000.0)


    def theaterChaseRainbow(self, wait_ms=50):
        """Rainbow movie theater light style chaser animation."""
        for j in range(256):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, self.wheel((i + j) % 255))
                self.strip.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, 0)

