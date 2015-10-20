#!/usr/bin/env python
from gopigo import *
from subprocess import call
import sys

f = open('tt', "w")
call(['espeak', 'starting'], stdout = f, stderr = f)
servo(75)
for count in range(0,3):
	led_on(1)
	time.sleep(0.1)
	led_on(0)
	time.sleep(0.2)
	led_off(1)
	time.sleep(0.1)
	led_off(0)
	time.sleep(0.2)

call(['espeak', 'now'], stdout = f, stderr = f)
