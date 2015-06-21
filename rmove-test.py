import signal
from kbhit import KBHit
from rmove import *

def signalHandler(signum, frame):
	if signum in [signal.SIGINT, signal.SIGTERM]:
		global stop_now
		stop_now = True

stop_now = False
signal.signal(signal.SIGINT, signalHandler)
signal.signal(signal.SIGTERM, signalHandler)
m = Move()
kb = KBHit()

print ("press jkl to move left, straight, right, m to stop, ESC to exit")

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
        elif ord(c) == 27:
            stop_now = True
    m.course_correct()
    time.sleep(0.1)
print('stop')
stop()
