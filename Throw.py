from pynput.keyboard import Listener
import meArm
import time

arm = meArm.meArm() # takes inserted data from meArm.py aka calibration data
arm.begin(0,0x70) #

# Idle Position
xi = -15 # x coordinate
yi = 175 # y coordinate
zi = -50 # z coordinate
# Pre Start
xp =  xi+20 # x coordinate
yp =  yi-20 # y coordinate
zp = 110 # z coordinate
# Start Position
xs =  95 # 155x coordinate
ys =  70 # 70y coordinate
zs =  zp # z coordinate
# End Position
xe =  70 # 40 70x coordinate
ye = 185 # 195 185 y coordinate
ze =  70 # z coordinate

arm.goDirectlyTo(arm.x,arm.y-25,arm.z)
time.sleep(0.5)
arm.goDirectlyTo(xi,yi,zi)
ready_toThrow = True


def on_press(key):
    global xs,ys,zs, xe,ye,ze
    var = str(format(key))
    semi = '\';\''
    
    if var == semi: ## PARIALLY opens gripper, to percentage (inputed, default is 50% but this can be modified) of full open state when ";" key is pressed
        if ready_toThrow:
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
        
    pass

def on_release(key):
    pass

with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
    