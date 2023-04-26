# Open Computer Vision and Numpy
import cv2

cv2.startWindowThread()

# Camera
camera_num =0

# Windows
cam = cv2.VideoCapture(camera_num, apiPreference=cv2.CAP_DSHOW)
# MAC
# cam = cv2.VideoCapture(camera_num, apiPreference=cv2.CAP_AVFOUNDATION)

# Image processor
# process = GripPipeline()

# Set Camera
width = 320
height = 240
fps = 30
exposure = 10000 # in microseconds
autoexposure = 0 # 0 will enable it
# Apply settings to camera
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cam.set(cv2.CAP_PROP_EXPOSURE, exposure)
cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, autoexposure)
cam.set(cv2.CAP_PROP_FPS, fps)

# Opens the camera settings window
cam.set(cv2.CAP_PROP_SETTINGS, 0.0)

# Display Ball Location with Circle
radius = 20
color = (255, 0, 0)
thickness = 2

# Main Loop
stop = False
while (not stop):
    ret, img = cam.read()

    # Your code goes here
    # process.process(img)
    # process.filter_contours_output

    # Need to find center of ball
    # display center of ball
    # img = cv2.circle(img, (x,y), radius, color, thickness) # check if x,y is correct order

    cv2.imshow("Camera", img)    

    try:    
        if (cv2.waitKey(1) & 0xFF == ord('q')) or (cv2.getWindowProperty("Camera", 0) < 0): stop = True
    except: stop = True  

cv2.destroyAllWindows()
