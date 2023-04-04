#!/usr/bin/python3

# To make this work:
# sudo apt install -y python3-picamera2
# disable legacy support in sudo raspi-config interfaces
# reboot

import cv2
from picamera2 import Picamera2

cv2.startWindowThread()

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

process = WhiteBall()

font = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 0.25
color = (0, 255, 0)
thickness = 1

# Main Loop
stop = False

while (not stop):
    img = picam2.capture_array()
    display_img = cv2.resize(img, ((int)(320), (int)(240)), 0, 0)
    
    # process.process(img)

    cv2.imshow("Camera", display_img)
    try:
        if (cv2.waitKey(1) & 0xFF == ord('q')) or (cv2.getWindowProperty("Camera", 0) < 0): stop = True
    except: stop = True 

cv2.destroyAllWindows()
