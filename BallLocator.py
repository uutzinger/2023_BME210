#!/usr/bin/python3

# To make this work:
# sudo apt install -y python3-picamera2
# sudo raspi-config
# and disable legacy camera support

import cv2
from picamera2 import Picamera2
from grip import WhiteBall

cv2.startWindowThread()

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

process = WhiteBall()

font = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 0.5
color = (0, 255, 0)
thickness = 1

width =  320
height = 240
startX =  25
startY = 100
endX =   295
endY =   240

# Main Loop
stop = False

while (not stop):
    img = picam2.capture_array()

    display_img = cv2.resize(img, ((int)(width), (int)(height)), 0, 0, cv2.INTER_CUBIC)
    
    # Extract ROI
    proc_img = display_img[startY:endY,startX:endX,:] 

    process.process(proc_img)

    if len(process.ball) > 0:
        x = process.ball[1] + startX
        y = process.ball[2] + startY
        area = process.ball[3]
        circ = process.ball[4]  
        approx = process.ball[5] 
        hsv = cv2.cvtColor(display_img, cv2.COLOR_BGR2HSV)
        cv2.drawMarker(display_img, (x, y),  (0, 0, 255), cv2.MARKER_CROSS, 10, 1)
        txt = "{:3n},{:3n},{:3n}".format(hsv[y,x,0], hsv[y,x,1], hsv[y,x,2])
        cv2.putText(display_img, txt, (x,y), font, fontScale, color, thickness, cv2.LINE_AA)
        txt = "{:3n},{:3.2f},{:3n}".format(area, circ, approx)
        cv2.putText(display_img, txt, (x,y+15), font, fontScale, color, thickness, cv2.LINE_AA)
        
    if len(process.filter_contours_output) > 0:
        # fix the offset of the region of interest
        for contour in process.filter_contours_output:
            # contour with new offset is created
            contour += (startX, startY)
        cv2.drawContours(display_img, process.filter_contours_output, -1, (0,255,0), 1)

    cv2.rectangle(display_img, (startX, startY), (endX, endY), (255,0,0), 2)
    cv2.imshow("Camera", display_img)
    try:
        if (cv2.waitKey(1) & 0xFF == ord('q')) or (cv2.getWindowProperty("Camera", 0) < 0): stop = True
    except: stop = True 

cv2.destroyAllWindows()