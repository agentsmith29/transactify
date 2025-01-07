import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18, GPIO.OUT)
f = 8e3
time_wait = 1/f
while True:
  
    GPIO.output(18, GPIO.LOW)
    time.sleep(time_wait/2)
    GPIO.output(18, GPIO.HIGH)
    time.sleep(time_wait/2)