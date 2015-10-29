#!/usr/bin/env python

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
    #speak("click")
    camera.capture(rawCapture, format = 'bgr', use_video_port = True)
    image = rawCapture.array
    center, poly, num_good, img = finder.find(image)
    #cv2.imshow('Frame', img)
    #cv2.waitKey(1000)
    if poly != None and finder.is_reasonable(poly):
        return center
    else:
        return None

def go_back():
    set_left_speed(100)
    set_right_speed(100)
    bwd()
    time.sleep(1)
    stop()
    time.sleep(.1)

def pick_random_direction(): #return True if found a good direction, False otherwise
    min_dist_to_go = 40 #less than that - turn again
    stop()
    time.sleep(.1)
    set_speed(100)
    for attempts in range(4): #try to turn 4 times, if all fail go back
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
        #speak("bump")
    speak("bump")
    go_back()
    return False

def go_somewhere(m, camera, rawCapture, finder): #go to a new place
    min_time_to_go = 5
    max_time_to_go = 10
    min_dist = 40

    if not pick_random_direction():
        return False

    time_to_go = random.randint(min_time_to_go, max_time_to_go)
    #speak("go for" + str(time_to_go))
    tstart = time.time()
    m.move(1, 200)
    while (time.time() - tstart < time_to_go):
        #time.sleep(.1)
        m.course_correct()
        pos = identify_object(camera, rawCapture, finder)
        if (pos != None):
            return True
        dist = us_dist(15)
        if dist < min_dist:
            m.stop()
            #time.sleep(.1)
            speak ("bump")
            go_back()
            return True
    m.stop()
    #speak("gone far enough")
    time.sleep(.1)
    return True

def look_around(camera, rawCapture, finder):
    #speak("look straight")
    enable_servo()
    servo(75)
    time.sleep(0.3)
    disable_servo()
    pos = identify_object(camera, rawCapture, finder)
    if pos != None:
        return pos
    #speak("look left")
    enable_servo()
    servo(140)
    time.sleep(0.3)
    disable_servo()
    pos = identify_object(camera, rawCapture, finder)
    if pos != None:
        return pos
    #speak("look right")
    enable_servo()
    servo(10)
    time.sleep(0.3)
    disable_servo()
    pos = identify_object(camera, rawCapture, finder)
    if pos != None:
        return pos
    enable_servo()
    servo(75)
    time.sleep(0.3)
    disable_servo()
    return None

def roam(camera, rawCapture, finder):
    m = Move()
    m.stop()
    while True:
        pos = look_around(camera, rawCapture, finder) #use that to look left and right
        #pos = identify_object(camera, rawCapture, finder)
        if (pos != None):
            return pos
        go_somewhere(m, camera, rawCapture, finder)
    return None

def want_to_play(camera, rawCapture, finder):
    time_to_wait = 10
    speak("want to play?")
    tstart = time.time()
    while (time.time() - tstart < time_to_wait):
        #speak("click")
        pos = identify_object(camera, rawCapture, finder)
        if pos != None:
            speak("yey! let's play")
            return True
        time.sleep(0.2)
    speak("boring")
    return False

camera, rawCapture = init_camera()
finder = findSymbol("/home/pi/MyGPG/gopigo-bw.jpg")
enable_servo()
servo(75)
time.sleep(0.3)
disable_servo()
if want_to_play(camera, rawCapture, finder):
    speak("O.K., now hide")
    time.sleep(5)
    speak("let's go seek")
    pos = roam(camera, rawCapture, finder)
    if (pos == None):
        speak("sorry, I'm too tired")
    else:
        speak ("yey, found it")
