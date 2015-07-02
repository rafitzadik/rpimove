#!/usr/bin/env python
import signal
from kbhit import KBHit
from rmove import *
import time

def signalHandler(signum, frame):
	if signum in [signal.SIGINT, signal.SIGTERM]:
		global stop_now
		stop_now = True

dist_to_stop = 20
stop_now = False
signal.signal(signal.SIGINT, signalHandler)
signal.signal(signal.SIGTERM, signalHandler)
m = Move()
kb = KBHit()

print ("press jkl to move left, straight, right, i to go back, m to stop, ESC to exit")

while not stop_now:
    if (kb.kbhit()):
        c = kb.getch()
        if c == 'j':
            print "left"
            m.move(0.5, 100)
        elif c == 'l':
            print "right"
            m.move(2, 100)
        elif c == 'k':
            print "straight"
            m.move(1, 200)
        elif c == 'm':
            print "stop"
            m.stop()
	elif c == 'i':
            print "back"
            m.stop()
	    set_left_speed(100)
	    time.sleep(0.1)
	    set_right_speed(100)
	    bwd()
        elif ord(c) == 27:
            stop_now = True
    dist = us_dist(15)
    if (dist < dist_to_stop):
	    print "too close. stop and back up"
	    m.stop()
	    set_left_speed(100)
	    time.sleep(0.1)
	    set_right_speed(100)
	    bwd()
	    time.sleep(1)
	    m.stop()
    m.course_correct()
    time.sleep(0.1)
print('stop')
stop()
