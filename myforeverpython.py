# Importing libraries

import time             # import timing
import RPi.GPIO as GPIO # import Raspberry Pi input out put

# Global Variables

# Buttons
blink_pin  = 16

# Initialize Button and Switch
GPIO.setmode(GPIO.BCM)
# Button is input
GPIO.setup(blink_pin, GPIO.OUT)

stopped  = False
while not stopped:
    GIPO.output(blink_pin, GPIO.HIGH)
    time.sleep(0.5)
    GIPO.output(blink_pin, GPIO.LOW)
    time.sleep(0.5)

GPIO.cleanup()
