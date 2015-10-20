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
from find_symbol import findSymbol

def speak(sentence):
    f = open('tt', "w")
    call(['espeak', sentence], stdout = f, stderr = f)
    f.close()

def init_camera():
    camera = PiCamera()
    rawCapture = PiRGBArray(camera)
    return camera, rawCapture

def identify_object(camera, rawCapture, finder):
    rawCapture.truncate(0)
    speak("click")
    camera.capture(rawCapture, format = 'bgr', use_video_port = True)
    image = rawCapture.array
    center, poly, num_good, img = finder.find(image)
    #cv2.imshow('Frame', img)
    #cv2.waitKey(1000)
    if poly != None and finder.is_reasonable(poly):
        return center
    else:
        return None

def pick_random_direction(): #return True if found a good direction, False otherwise
    min_dist_to_go = 40 #less than that - turn again
    stop()
    set_speed(100)
    for attempts in range(4): #try to turn 4 times, if all fail break
        turn_time = random.randint(3,15) #how long to turn
        turn_dir = random.randint(0,1) #left or right?
        if (turn_dir == 0):
            #speak("turn left for " + str(turn_time))
            left() #robot starts turning left
        else:
            #speak("turn right for " + str(turn_time))
            right()
        #now let the robot turn
        time.sleep(.1 * turn_time)
        stop()
        time.sleep(.1)
        #is there enough distance in this direction?
        dist = us_dist(15)
        if dist > min_dist_to_go:
            return True
        speak("bump")
    speak("obstacles everywhere, this is too much")
    return False

def go_somewhere(m): #go to a new place
    min_time_to_go = 2
    max_time_to_go = 6
    min_dist = 40

    if not pick_random_direction():
        return False

    time_to_go = random.randint(min_time_to_go, max_time_to_go)
    #speak("go for" + str(time_to_go))
    tstart = time.time()
    m.move(1, 200)
    while (time.time() - tstart < time_to_go):
        time.sleep(.1)
        m.course_correct()
        dist = us_dist(15)
        if dist < min_dist:
            m.stop()
            speak ("bump")
            return True
    m.stop()
    #speak("gone far enough")
    return True

def look_around(camera, rawCapture, finder):
    speak("look straight")
    servo(75)
    time.sleep(0.2)
    pos = identify_object(camera, rawCapture, finder)
    if pos != None:
        return pos
    speak("look left")
    servo(140)
    time.sleep(0.2)
    pos = identify_object(camera, rawCapture, finder)
    if pos != None:
        return pos
    speak("look right")
    servo(10)
    time.sleep(0.2)
    pos = identify_object(camera, rawCapture, finder)
    if pos != None:
        return pos
    servo(75)
    time.sleep(0.2)

def roam(camera, rawCapture, finder):
    m = Move()
    m.stop()
    servo(75)
    time.sleep(0.2)
    while True:
        #pos = look_around(camera, rawCapture, finder) #use that to look left and right
        pos = identify_object(camera, rawCapture, finder)
        if (pos != None):
            return pos
        go_somewhere(m)
    return None

speak("let's go seek")
camera, rawCapture = init_camera()
finder = findSymbol("gopigo-bw.jpg")
pos = roam(camera, rawCapture, finder)
if (pos == None):
    speak("sorry, I'm too tired")
else:
    speak ("yey, found it")
