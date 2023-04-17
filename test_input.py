# Importing libraries

import time             # import timing
import RPi.GPIO as GPIO # import Raspberry Pi input out put

# Global Variables

# Buttons
start_pin  = 21

# Switch
switch_pin = 20

# Initialize Button and Switch
GPIO.setmode(GPIO.BCM)
# Button is input
GPIO.setup(start_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

stopped  = False
while stopped != True:
    switch_state = GPIO.input(switch_pin)
    start_state = GPIO.input(start_pin)
    str_start = "pushed" if start_state else "not pushed"
    str_switch = "Defense" if switch_state else "Attack"
    print("Start is {} and Switch is {}".format(str_start, str_switch))
    time.sleep(0.05)

GPIO.cleanup()
