from rmove import *
from gopigo import *

# Go straight for 5 seconds, then blink leds and stop

m = Move()

m.move(1, 100)
for i in range(0,40):
	m.course_correct()
	time.sleep(0.1)
m.stop()
time.sleep(0.1)
for count in range(0,3):
	led_on(1)
	time.sleep(0.1)
	led_on(0)
	time.sleep(0.2)
	led_off(1)
	time.sleep(0.1)
	led_off(0)
	time.sleep(0.2)
