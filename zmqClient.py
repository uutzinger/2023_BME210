import zmq
import time
import pickle

port = 5555

class Point(object):
    def __init__(self, x=0., y=0.):
        self.x = x
        self.y = y

# Allocate the location object
ball_loc = Point()

#  Socket to talk to server
context = zmq.Context()
print("Connecting to server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:{:d}".format(port)) # localhost is your computer

while True:
    socket.send_string("loc")
    #  Get the reply
    p = socket.recv()
    ball_loc = pickle.loads(p) # deserialize the ball_loc object
    print("Location x:{}, y:{}".format(ball_loc.x, ball_loc.y))
    time.sleep(0.1)
    # Here goes your meArm stuff
    # ... ball_loc.x
    # ... ball_loc.y
