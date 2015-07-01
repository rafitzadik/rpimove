# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from find_blue import find_blue
import signal
from kbhit import KBHit
from gopigo import *
from rmove import *
import time
import cv2

kb = KBHit()
xres = 320
yres = 240
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (xres, yres)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(xres, yres))
m = Move()
dist_to_stop = 20
direction = -1
max_time_to_run = 10
threshold_to_change_direction = 40
show_frame_rate = 0 #0 to not show a window, otherwise show 1:n frames

# allow the camera to warmup
time.sleep(0.1)
i = 0
tstart = time.clock()

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image
    image = frame.array
    # find the feature we're looking for
    (x,y),(rx,ry,w,h) = find_blue(image)

    # if found the feature:
    if (x != -1):
        #print(x - (xres / 2))
        if (show_frame_rate != 0 and i % show_frame_rate == 0):
            # show the frame
            cv2.rectangle(image, (rx,ry), (rx+w, ry+h), (0, 255, 0), 2)
            cv2.circle(image, (x, y), 3, (0,0,255), -1)
            cv2.imshow("Frame", image)
            cv2.waitKey(1)
        # find direction to go
        if ((x - (xres / 2)) < -threshold_to_change_direction): #target is to the right
            new_direction = 0.9
        elif ((x - (xres / 2)) > threshold_to_change_direction): #target is to the left
            new_direction = 1.1
        else:
            new_direction = 1
        # do we need to change direction?
        if new_direction != direction:
            if new_direction > 1:
                print ("right", x - (xres / 2))
            elif new_direction < 1:
                print ("left", x - (xres / 2))
            else:
                print ("straight")
            direction = new_direction
            m.move(direction, speed=70)
        else:
            m.course_correct()
        dist = us_dist(15)
        if (dist < dist_to_stop):
            print("too close, stop")
            m.stop()
            break
    else: # we could not find the target - stop and wait
        m.stop
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    i = i+1
    time.sleep(0.1) #allow the system some time - don't hog the CPU
    # if the `q` key was pressed, break from the loop
    if (kb.kbhit()):
        c = kb.getch()
        if (c == 'q'):
            break
    if ( (time.clock() - tstart) > max_time_to_run):
        break

print("fps: ", i / (time.clock() - tstart), i, time.clock() - tstart)
m.stop()
cv2.destroyAllWindows()
print("out")
