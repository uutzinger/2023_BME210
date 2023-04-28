#!/usr/bin/python3
##############################################################################
# BME 210 2023
# Game Play Skeleton
##############################################################################
##############################################################################
# Urs Utzinger 4/14/2023
##############################################################################

DEBUG = True
DISPLAY = True
TEXT_DEBUG = False

############
# Imports
############

import cv2
import numpy as np
import math
import time
from copy import copy
from picamera2 import Picamera2
import RPi.GPIO as GPIO # import Raspberry Pi input out put
import meArm

##############################################################################
#  Setup
##############################################################################
                     

##############################################################################
# Initialize
##############################################################################

# Initialize Button and Switch
GPIO.setmode(GPIO.BCM)
# Button is input
GPIO.setup(start_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

##############################################################################
# Main Loop
##############################################################################

# Main Loop
#########################################################
stop = False
ready_toThrow = False

while (not stop):
    
    # Read Switch
    start_state  = GPIO.input(start_pin)
    switch_state = GPIO.input(switch_pin)
    str_start    = "pushed" if start_state else "not pushed"
    str_switch   = "Defense" if switch_state else "Attack"
    if TEXT_DEBUG: print("Start is {} and Switch is {}".format(str_start, str_switch))

    if switch_state:
        ####################################################
        # Defense
        ####################################################

        ready_toThrow = False

        ####################################################
        # Detect Ball
        ####################################################
        
        ######################################
        # Move Arm depending on Ball Location
        ######################################
        
    else:

        ####################################################
        # Attack
        ####################################################
        if ready_toThrow == False:
          ready_toThrow = True
          pass # replace with your own code
        if start_state and ready_toThrow:
          pass # replace with your own code

# Clean up
GPIO.cleanup()
