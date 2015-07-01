import signal
from kbhit import KBHit
from rmove import *

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
print ("if an obstacle is detected, the robot will stop and backup")
while not stop_now:
    if (kb.kbhit()):
        c = kb.getch()
        if c == 'j':
            m.move(0.5)
        elif c == 'l':
            m.move(2)
        elif c == 'k':
            m.move(1)
        elif c == 'm':
            m.stop()
	elif c == 'i':
            m.stop()
	    set_left_speed(100)
	    set_right_speed(100)
	    bwd()
        elif ord(c) == 27:
            stop_now = True
    dist = us_dist(15)
    if (dist < dist_to_stop):
	    m.stop()
	    set_left_speed(100)
	    set_right_speed(100)
	    bwd()
	    time.sleep(0.5)
	    m.stop()
    m.course_correct()
    time.sleep(0.1)
print('stop')
stop()
