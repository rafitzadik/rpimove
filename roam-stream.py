# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import signal
from kbhit import KBHit
from subprocess import call
from gopigo import *
from rmove import *
import random
import time
import cv2

def speak(sentence):
    f = open('tt', "w")
    call(['espeak', sentence], stdout = f, stderr = f)
    f.close()

def pick_random_direction(): #return True if found a good direction, False otherwise
    min_dist_to_go = 40 #less than that - turn again
    stop()
    set_speed(100)
    for attempts in range(4): #try to turn 4 times, if all fail break
        turn_time = random.randint(3,15) #how long to turn
        turn_dir = random.randint(0,1) #left or right?
        if (turn_dir == 0):
            speak("turn left for " + str(turn_time))
            left() #robot starts turning left
        else:
            speak("turn right for " + str(turn_time))
            right()
        #now let the robot turn
        time.sleep(.1 * turn_time)
        stop()
        time.sleep(.1)
        #is there enough distance in this direction?
        dist = us_dist(15)
        if dist > min_dist_to_go:
            return True
        speak("distance is too short, retry")
    speak("failed to find a free place to turn")
    return False

kb = KBHit()
xres = 320
yres = 240

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (xres, yres)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(xres, yres))
# allow the camera to warmup
time.sleep(0.1)

# initialize the movement
m = Move()
dist_to_stop = 40
max_time_to_go = 50 #in frames
direction = -1
max_time_to_run = 120 #in seconds
ch = ' '

speak ("starting")
pick_random_direction()
time_to_go = random.randint(1, max_time_to_go)
speak("go for " + str(time_to_go))
m.move(1, 200)

i = 0
tstart = time.time()

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image
    image = frame.array
    cv2.imshow("Frame", image)
    ch = cv2.waitKey(1) & 0xff

    time_to_go = time_to_go - 1
    dist = us_dist(15)
    if (time_to_go == 0) or dist < dist_to_stop:
        m.stop()
        if (time_to_go == 0):
            speak("time to change direction")
        else:
            speak("too close, stop and change direction")
        if (not pick_random_direction()):
            #failed to find a good direction
            break
        time_to_go = random.randint(1, max_time_to_go)
        speak("go for " + str(time_to_go))
        m.move(1,200)

    m.course_correct()
    time.sleep(0.1)
    rawCapture.truncate(0)
    i = i+1
    # if the `q` key was pressed, break from the loop
    if ch == ord('q'):
        break
    if (kb.kbhit()):
        c = kb.getch()
        if (c == 'q'):
            break
    if ( (time.time() - tstart) > max_time_to_run):
        speak("time limit reached")
        break

print("fps: ", i / (time.time() - tstart), i, time.time() - tstart)
m.stop()
cv2.destroyAllWindows()
print("out")
