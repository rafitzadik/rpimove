#!/usr/bin/env python
from gopigo import *
import sys

import atexit
atexit.register(stop)

for count in range(0,3):
	led_on(1)
	time.sleep(0.1)
	led_on(0)
	time.sleep(0.2)
	led_off(1)
	time.sleep(0.1)
	led_off(0)
	time.sleep(0.2)
