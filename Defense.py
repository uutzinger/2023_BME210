#!/usr/bin/python3

# To make this work you will need
#1)
# sudo apt install -y python3-picamera2
# sudo raspi-config
# and disable legacy camera support
#2)
# meArm.py and kinematics.py and grip.py
# in the same folder as this program
#
# Urs Utzinger 4/14/2023

############
# Camera
############

import cv2
#import numpy as np
from picamera2 import Picamera2
from grip import WhiteBall

cv2.startWindowThread()

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

process = WhiteBall()

font = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 0.25
color = (0, 255, 0)
thickness = 1

width =  320
height = 240
startX =   0
startY = 100
endX =   320
endY =   200

#############
# meArm
#############

from pynput.keyboard import Listener
import meArm
import time

arm = meArm.meArm() # takes inserted data from meArm.py aka calibration data
arm.begin(0,0x70) #

# Idle Position
xi = 145
yi =  60
zi = 110

# Defense
#########
x_offset = 0     # depends on your position in the field
x_gain   = -1    # depends on the distance and camera angle
z_offset = 0     # depends on the distance and camera angle
z_gain   = 0.5   # might need to be same as x_gain but opposite sign
motor_y  = 180   # defines the position from the goal during defense

# Throwing
##############
# Start Position
xs = 145 # x coordinate
ys =  60 # y coordinate
zs = 110 # z coordinate
# End Position
xe =   0 # x coordinate
ye = 195 # y coordinate
ze =  90 # z coordinate

import collections
import statistics
# this will slow response down, perhaps better to not filter
pos_x = collections.deque(maxlen=3) # if you want to take median of 3 locations. 
pos_y = collections.deque(maxlen=3)
pos_x.append(x_offset) # initialize
pos_y.append(z_offset)

# Initilize the arm and camera
arm.gotoPoint(xi,yi,zi) 

# Main Loop
stop = False

while (not stop):

    #####
    # Detect Ball
    #####
    img = picam2.capture_array()
    display_img = cv2.resize(img, ((int)(width), (int)(height)), 0, 0, cv2.INTER_CUBIC)
    # Extract ROI
    proc_img = display_img[startY:endY,startX:endX,:] 
    # Process the image to find ball
    process.process(proc_img)
    # Display ball
    if len(process.ball) > 0:
        x = process.ball[1] + startX
        y = process.ball[2] + startY
        # pos_x = x # no filtering
        # pos_y = y
        pos_x.append(x)
        pos_y.append(y)
        area = process.ball[3]
        circ = process.ball[4]  
        approx = process.ball[5] 
        hsv = cv2.cvtColor(display_img, cv2.COLOR_BGR2HSV)
        cv2.drawMarker(display_img, (x, y),  (0, 0, 255), cv2.MARKER_CROSS, 10, 1)
        txt = "{:3n},{:3n},{:3n}".format(hsv[y,x,0], hsv[y,x,1], hsv[y,x,2])
        cv2.putText(display_img, txt, (x,y), font, fontScale, color, thickness, cv2.LINE_AA)
        txt = "{:3n},{:3.2f},{:3n}".format(area, circ, approx)
        cv2.putText(display_img, txt, (x,y+8), font, fontScale, color, thickness, cv2.LINE_AA)

    # Display all contours found
    if len(process.filter_contours_output) > 0:
        # fix the offset of the region of interest
        for contour in process.filter_contours_output:
            # contour with new offset is created
            contour += (startX, startY)
        cv2.drawContours(display_img, process.filter_contours_output, -1, (0,255,0), 1)
    # Show region of interest
    cv2.rectangle(display_img, (startX, startY), (endX, endY), (255,0,0), 2)
    cv2.imshow("Camera", display_img)

    # Check if user want to quit
    try:
        if (cv2.waitKey(1) & 0xFF == ord('q')) or (cv2.getWindowProperty("Camera", 0) < 0): stop = True
    except: stop = True 

    ####
    # Move Arm depending on Ball Location
    ####
    ball_x=statistics.median(pos_x)
    ball_y=statistics.median(pos_y)
    # ball_x = pos_x # no filtering
    # ball_y = pos_y
    motor_x = x_gain*(width/2 -ball_x) + x_offset
    motor_z = z_gain*(height  -ball_y) + z_offset
    # print("{},{}".format(motor_x,motor_z))
    arm.goDirectlyTo(motor_x, motor_y, motor_z)

# Clean up
cv2.destroyAllWindows()