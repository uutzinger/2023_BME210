#!/usr/bin/python3
##############################################################################
# BME 210 2023
# Game Play
##############################################################################
# To make this work you will need
#1)
# sudo apt install -y python3-picamera2
# sudo raspi-config
# and disable legacy camera support
#2)
# meArm.py and kinematics.py
# in the same folder as this program
#3) 
# meArm.py calibrated as shown in class
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
                     
###########################    
# Settings Object Detection
###########################   

# Image Size and Location of Region of Interest ROI
###################################################
width =  320
height = 240
startX =  50
startY = 100
endX =   320-startX
endY =   240-30
0
# Region of Interest Histogtram square half width
w2  =  4   # half width of ROI
o_x =  0   # shift left/right from center
o_y = 25   # shift up down from center

# HSV Threshold
#########################################################
hue = [  0.0,  35.0] # average 120, in my office 160..170
sat = [  0.0,  40.0] # average 30,  in my office 25..35
val = [190.0, 255.0] # average 200, in my office  205..235

# Contrast Enhancement
######################
CLAHElimit = 3.0     # 2-10 is reasonable value

# Blur
######
blur_radius = 2      # 1-5 is reasonable value

# STD
######
std_window = 10      # 5-20 is reasonable value

# Erode
# Removes noise
###############    
iterations = 1       # 1-3 is reasonable value

# Contour detect
################
external_only = False

# Filter Contours
#################
min_area   = 20      # Minium ball area
max_area   = 100     # Maximum ball area
min_perimeter = 15   # Minimum ball perimeter
min_width  = 10      # Width and Height of box enclosing ball
max_width  = 50
min_height = 10              
max_height = 50
solidity = [60, 100] # Range for area/convex_hull_area in percent
max_vertices = 1000  # Number of vertices in a contour polygon
min_vertices = 2     #
min_ratio = 0.5      # Ratio of width to height
max_ratio = 2.0      # Circle has ratio of 1.0

# Ball Selection
################    
minCircularity = 0.2 # 0.0 - 1.0, circle has ratio of 1.0 (max area, min perimeter)
maxCircularity = 1.0
minApprox = 10       # 4-25, rectangle has smallest number
maxApprox = 25

# Buttons
###############
start_pin  = 21
# Switch
switch_pin = 20

# Defense
#########
x_offset = 0     # depends on your position in the field
x_gain   = -1    # depends on the distance and camera angle
z_offset = 0     # depends on the distance and camera angle
z_gain   = 0.5   # might need to be same as x_gain but opposite sign
motor_y  = 160   # defines the position from the goal during defense

# Max positions for defense
###########################
x_max = 40
x_min =-60
y_max = 180
y_min = 170
z_max = 70
z_min = 0

# Throwing
##############
ready_toThrow =  False
# Idle Position
xi =  -5 # x coordinate
yi = 175 # y coordinate
zi = -50 # z coordinate
# Pre Start
xp =  -5 # x coordinate
yp = 175 # y coordinate
zp = 110 # z coordinate
# Start Position
xs = 145 # x coordinate
ys =  60 # y coordinate
zs = 110 # z coordinate
# End Position
xe =   0 # x coordinate
ye = 195 # y coordinate
ze =  90 # z coordinate

# Text on display images
########################
font = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 0.5
color = (0, 0, 255)
thickness = 1

##############################################################################
#  Support Functions
##############################################################################
# define a function to compute and plot histogram
def plot_histogram(img, mask=None):
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 0.5
    color = (0, 0, 0)
    thickness = 1
    #Set hist parameters
    hist_height = 256
    hist_width = 512
    nbins = 64
    bin_width = int(hist_width/nbins)
    hist_img = np.zeros((hist_height,hist_width,3),dtype=np.uint8)
    # split the image into blue, green and red channels
    channels = cv2.split(img)
    # loop over the image channels
    for indx, channel in enumerate(channels):
        # compute the histogram for the current channel and plot it
        hist = cv2.calcHist([channel], [0], mask, [nbins], [0, 256])
        cv2.normalize(hist,hist,0,hist_height,cv2.NORM_MINMAX)      
        hist=np.int32(np.around(hist))
        tmp = hist_img[:,:,indx].copy()
        for x,y in enumerate(hist):
            cv2.rectangle(tmp,(x*bin_width,hist_height),(x*bin_width + bin_width-1,hist_height-y[0]),255,1)
        np.copyto(hist_img[:,:,indx],tmp)
    mask = cv2.inRange(hist_img, (0,0,0), (0,0,0))
    hist_img[mask>0]=(255,255,255)
    for loc in range(0,hist_width,25*hist_width//256):
        txt = str(int(loc/(hist_width/256)))
        cv2.putText(hist_img, txt, (loc,hist_height-5), font, fontScale, color, thickness, cv2.LINE_AA)
    
    cv2.putText(hist_img, '-H/B', (5,15), font, fontScale, (255,0,0), thickness, cv2.LINE_AA)
    cv2.putText(hist_img, '-S/G', (5,30), font, fontScale, (0,255,0), thickness, cv2.LINE_AA)
    cv2.putText(hist_img, '-V/R', (5,45), font, fontScale, (0,0,255), thickness, cv2.LINE_AA)

    return hist_img

##############################################################################
# Initialize
##############################################################################

if DEBUG or DISPLAY: cv2.startWindowThread()

arm = meArm.meArm() # takes inserted data from meArm.py aka calibration data
arm.begin(0,0x70) #

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

# Initialize Button and Switch
GPIO.setmode(GPIO.BCM)
# Button is input
GPIO.setup(start_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

##############################################################################
# Main Loop
##############################################################################

pos_x = x_offset
pos_y = z_offset
stop = False

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
        
        img = picam2.capture_array()
        img=img[:,:,0:3]

        display_img = cv2.resize(img, ((int)(width), (int)(height)), 0, 0, cv2.INTER_CUBIC)
        
        # Extract ROI
        # We dont want to search for ball in the whole image
        ########################################    
        proc_img = copy(display_img[startY:endY,startX:endX,:])
        if DEBUG:
            cv2.imshow("Proc", proc_img)

        # Adaptive local contrast enhancement
        # (Contrast Limited Adaptive Histogram Equalization
        ########################################    
        hsv_img=cv2.cvtColor(proc_img, cv2.COLOR_BGR2HSV)
        h,w=hsv_img.shape[:2]
        clahe = cv2.createCLAHE(clipLimit=CLAHElimit, tileGridSize=(int(h/32), int(w/32)))
        hsv_img[:,:,2] = clahe.apply(hsv_img[:,:,2])

        # Blur
        ########################################    
        blur_img = cv2.medianBlur(hsv_img, int(2 * round(blur_radius) + 1))
        if DEBUG:
            cv2.imshow("Blur", cv2.cvtColor(blur_img, cv2.COLOR_HSV2BGR))

        # Color ROI for center of HSV image
        ########################################
        clahe_display_img = copy(blur_img)

        ROI_TL_X=int(w/2-w2-o_x)
        ROI_TL_Y=int(h/2-w2-o_y)
        ROI_BR_X=int(w/2+w2-o_x)
        ROI_BR_Y=int(h/2+w2-o_y)
        proc_roi = blur_img[ROI_TL_Y:ROI_BR_Y,ROI_TL_X:ROI_BR_X,:] 
        a = (np.mean(proc_roi, axis=(0,1))).astype(int)
        txt_hsv = "{:3n} | {:3n} | {:3n}".format(a[0], a[1], a[2])
        cv2.rectangle(clahe_display_img, (ROI_TL_X,ROI_TL_Y), (ROI_BR_X, ROI_BR_Y), (0,255,0), 1)
        cv2.putText(clahe_display_img, txt_hsv, (ROI_TL_X,ROI_TL_Y), font, fontScale, color, thickness, cv2.LINE_AA)
        if DEBUG:
            cv2.imshow("CLAHE", cv2.cvtColor(clahe_display_img, cv2.COLOR_HSV2BGR))  

        # Histogram
        ########################################    
        if DISPLAY:
            hist_img=plot_histogram(proc_roi)
            cv2.imshow("ROI Histogram", hist_img)

        # # Images areas with similar color
        # ##################################
        # # tic = time.perf_counter()
        # std_scale=2
        # std_img = cv2.resize(blur_img, ((int)(w/std_scale), (int)(h/std_scale)), 0, 0, cv2.INTER_CUBIC)
        # pw= int(std_window/std_scale/2)
        # std_img= np.pad(std_img, ((pw,pw), (pw,pw), (0,0)), 'reflect')
        # img_rolled = np.lib.stride_tricks.sliding_window_view(std_img, (int(std_window/std_scale),int(std_window/std_scale)), axis=(0,1))
        # std_img = np.std(img_rolled, axis=(3,4))
        # std=np.sqrt(np.sum((std_img*std_img),axis=2))
        # std=np.uint8(255.*std/np.max(std))
        # std_img = cv2.resize(std, ((int)(w), (int)(h)), 0, 0, cv2.INTER_CUBIC)
        # # toc = time.perf_counter()
        # # print((toc-tic)*1000)
        # if DEBUG:
        #     cv2.imshow("STD", std_img)

        # HSV Threshold
        ########################################    
        hsv_thresh = cv2.inRange(hsv_img, (hue[0], sat[0], val[0]),  (hue[1], sat[1], val[1]))
        if DEBUG:
            cv2.imshow("HSV Thresh", hsv_thresh)   

        # Erode/Dilate
        ########################################    
        kernel = None
        anchor = (-1, -1)
        border_type = cv2.BORDER_CONSTANT
        border_value = (-1)
        # Erode away
        erode_img = cv2.erode(hsv_thresh, kernel, anchor, iterations = (int) (iterations +0.5),
                    borderType = border_type, borderValue = border_value)
        # Dilate back
        erode_img = cv2.dilate(erode_img, kernel, anchor, iterations = (int) (iterations +0.5),
                    borderType = border_type, borderValue = border_value)

        if DEBUG:   
            cv2.imshow("Erode", erode_img)   

        # Contour detect
        ########################################    
        if(external_only):
            mode = cv2.RETR_EXTERNAL
        else:
            mode = cv2.RETR_LIST
        method = cv2.CHAIN_APPROX_SIMPLE
        contours, hierarchy =cv2.findContours(erode_img, mode=mode, method=method)

        if DEBUG:
            for contour in contours:
                cv2.drawContours(proc_img, contours, -1, (0,255,0), 1)

        # Filter Contours
        ########################################    
        candidates_contour  = []
        candidates_hull     = []        
        candidates_features = []
        for contour in contours:
            # Bounding rectangle
            x,y,w,h = cv2.boundingRect(contour)
            if (w < min_width or w > max_width):
                continue
            if (h < min_height or h > max_height):
                continue
            # Area
            area = cv2.contourArea(contour)
            if (area < min_area or area > max_area):
                continue
            # perimeter
            perimeter = cv2.arcLength(contour, True)  
            if perimeter < min_perimeter:
                continue
            # Hull of contour
            hull = cv2.convexHull(contour) # contour without indentations
            # Solidity
            solid = 100 * area / cv2.contourArea(hull) # dont want indentations in contour
            if (solid < solidity[0] or solid > solidity[1]):
                continue
            if (len(contour) < min_vertices or len(contour) > max_vertices):
                continue
            # Aspect ratio of bounding box
            ratio = (float)(w) / h # the closer to 1 the more likely its a circle
            if (ratio < min_ratio or ratio > max_ratio):
                continue
            # Circularity
            circularity  = 4.*math.pi* area/perimeter/perimeter # the closer to 1 the more likely its a circle
            if circularity < minCircularity or circularity > maxCircularity:
                continue
            # Compute simplified contour (minimum vertices)
            approx = len(cv2.approxPolyDP(contour,0.01*perimeter,True)) # the smaller the more likley its a circle
            # Compute moments to determine center of contour
            MM = cv2.moments(contour)
            cX = int(MM["m10"] / MM["m00"])
            cY = int(MM["m01"] / MM["m00"])

            candidates_contour.append(contour)
            candidates_hull.append(hull)        
            candidates_features.append([cX, cY, area, perimeter, 
                                        circularity, approx, ratio, solid, 
                                        (1-circularity) * approx])

        if DEBUG:
            for contour in candidates_contour:
                cv2.drawContours(proc_img, contour, -1, (0,0,255), 2)

            cv2.imshow("Contours", proc_img) 
        
        # Find object that fits "the best"
        if len(candidates_features) > 0:
            # Sort by score which is feature at last column of list, 
            # Sort so that smallest feature is on top of list
            candidates_features.sort(reverse=True, key=lambda x: x[-1])
            # print(candidates[0])
        
        # # Hough Circles (Test)
        # ########################################    
        # # channels=cv2.split(blur_img)
        # # gray = channels[2]
        # # gray = 255-gray
        # gray = hsv_thresh
        # rows = gray.shape[0]
        # circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 2, rows / 4,
        #                            param1=50, param2=30,
        #                            minRadius=5, maxRadius=30)
        # hough_img = proc_img.copy()
        # if circles is not None:
        #     circles = np.uint16(np.around(circles))
        #     for i in circles[0, :]:
        #         center = (i[0], i[1])
        #         # circle center
        #         cv2.circle(hough_img, center, 1, (0,255,0), 3)
        #         # circle outline
        #         radius = i[2]
        #         cv2.circle(hough_img, center, radius, (0,0,255), 3)
        # if DEBUG:
        #     cv2.imshow("Hough", hough_img)   
                    
        # Display on Main Image
        ########################################    
        if DISPLAY:
            
            # copy the blurred and contrast enhanced image onto original image
            display_img[startY:endY,startX:endX,:] = cv2.cvtColor(blur_img, cv2.COLOR_HSV2BGR)
            
            # Draw all contours
            if len(contours) > 0:
                cv2.drawContours(display_img, contours, -1, (0,255,0), 1, offset=((startX, startY)))

            # Draw the filtered contours
            if len(candidates_contour) > 0:
                cv2.drawContours(display_img, candidates_contour, -1, (0,0,255), 2, offset=((startX, startY)))

            # Draw detected ball
            # [cX, cY, area, perimeter, circularity, approx, ratio, solid, (1-circularity) * approx]
            # Last item in above list is feature to detect contour most resembling a circle the smaller it is
            for i, ball in enumerate(candidates_features):
                x = ball[0] + startX
                y = ball[1] + startY
                area   = ball[2]
                perimeter = ball[3]
                circ   = ball[4]  
                approx = ball[5]
                ratio  = ball[6]
                solid  = ball[7] 
                score  = ball[8]
                if i==0:
                    cv2.drawMarker(display_img, (x, y),  (255, 0, 255), cv2.MARKER_CROSS, 10, 2)
                else:
                    cv2.drawMarker(display_img, (x, y),  (0, 0, 255), cv2.MARKER_CROSS, 10, 1)
                txt = "{:3n} | {:3.2f} | {:3n} | {:4.2f}".format(area, circ, approx, score)
                cv2.putText(display_img, txt, (x,y), font, fontScale, color, thickness, cv2.LINE_AA)

            # Draw where data for HSV histogram was taken from
            TL = (ROI_TL_X+startX,ROI_TL_Y+startY)
            BR = (ROI_BR_X+startX,ROI_BR_Y+startY)
            cv2.rectangle(display_img, TL, BR, (0,255,0), 1)

            # Draw processed Region of Interest
            cv2.rectangle(display_img, (startX, startY), (endX, endY), (255,0,0), 2)

            # Display the image twice as large to make it more visible
            display_img = cv2.resize(display_img, ((int)(2*width), (int)(2*height)), 0, 0, cv2.INTER_CUBIC)
            cv2.imshow("Camera", display_img)
        
        ######################################
        # Move Arm depending on Ball Location
        ######################################
        if len(candidates_features) > 0:
            ball=candidates_features[0]
            ball_x = ball[0]
            ball_y = ball[1]
            motor_x = x_gain*(width/2 -ball_x) + x_offset
            motor_z = z_gain*(height  -ball_y) + z_offset
            # print("{},{}".format(motor_x,motor_z))
            if motor_x > x_max: motor_x = x_max
            if motor_x < x_min: motor_x = x_min
            if motor_y > y_max: motor_y = y_max
            if motor_y < y_min: motor_y = y_min
            if motor_z > z_max: motor_z = z_max
            if motor_z < z_min: motor_z = z_min
                    
            arm.goDirectlyTo(motor_x, motor_y, motor_z)
        
    else:

        ####################################################
        # Attack
        ####################################################
        if ready_toThrow == False:
            arm.goDirectlyTo(arm.x,arm.y-25,arm.z)
            time.sleep(0.5)
            arm.goDirectlyTo(xi,yi,zi)
            ready_toThrow = True
        if start_state and ready_toThrow:
            # Ready ...
            arm.gotoPoint(xp,yp,zp)
            time.sleep(0.5)
            # Set ...
            arm.gotoPoint(xs,ys,zs)
            time.sleep(0.5)
            # Go!!
            arm.goDirectlyTo(xe,ye,ze)
            time.sleep(0.2)
            # Relax
            arm.gotoPoint(xi,yi,zi)

    if DISPLAY:
        try:
            # Obtain the key stroke if any occured
            k = cv2.waitKey(1) & 0xFF
            # Quit if q is pressed
            if (k == ord('q')) or (cv2.getWindowProperty("Camera", 0) < 0): 
                stop = True
            # Adjust HUV thresholds based on keystrokes
            # Hue
            elif k == ord('h'):
                hue = [hue[0]+5,hue[1]]
                print("Hue: {}".format(hue))
            elif k == ord('n'):
                hue = [hue[0],hue[1]+5]
                print("Hue: {}".format(hue))
            elif k == ord('j'):
                hue = [hue[0]-5,hue[1]]
                print("Hue: {}".format(hue))
            elif k == ord('m'):
                hue = [hue[0],hue[1]-5]
                print("Hue: {}".format(hue))
            # Sat
            elif k == ord('s'):
                sat = [sat[0]+5,sat[1]]
                print("Sat: {}".format(sat))
            elif k == ord('x'):
                sat = [sat[0],sat[1]+5]
                print("Sat: {}".format(sat))
            elif k == ord('d'):
                sat = [sat[0]-5,sat[1]]
                print("Sat: {}".format(sat))
            elif k == ord('c'):
                sat = [sat[0],sat[1]-5]
                print("Sat: {}".format(sat))
            # Val
            elif k == ord('f'):
                val = [val[0]+5,val[1]]
                print("Val: {}".format(val))
            elif k == ord('v'):
                val = [val[0],val[1]+5]
                print("Val: {}".format(val))
            elif k == ord('g'):
                val = [val[0]-5,val[1]]
                print("Val: {}".format(val))
            elif k == ord('b'):
                val = [val[0],val[1]-5]
                print("Val: {}".format(val))

        except: stop = True 

# Clean up
cv2.destroyAllWindows()
GPIO.cleanup()
