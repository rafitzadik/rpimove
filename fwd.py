#!/usr/bin/env python
#############################################################################################################                                                                  
# Rafi: Trying to move forward while reading the encoders and correcting for bias
##############################################################################################################

from gopigo import *	#Has the basic functions for controlling the GoPiGo Robot
import sys	#Used for closing the running program
import signal

def signalHandler(signum, frame):
	if signum in [signal.SIGINT, signal.SIGTERM]:
		global stop_now
		stop_now = True


stop_now = False
signal.signal(signal.SIGINT, signalHandler)
signal.signal(signal.SIGTERM, signalHandler)
lenc = enc_read(0)
renc = enc_read(1)
speed = 100
left_speed = 80 #On my GoPiGo this seems to work well
trim = 0.0
set_speed(speed)
time.sleep(0.1)
motor_fwd()
while not stop_now:
	time.sleep(0.1)
	nlenc = enc_read(0)
	nrenc = enc_read(1)
	print('left: ' + str(nlenc - lenc) + ' right: ' + str(nrenc - renc))
	if (nlenc != -1) and (lenc != -1) and (nrenc != -1) and (renc != -1): # all reading are valid
		if (nrenc > renc): # right wheel moved at all?
			trim = float(nlenc - lenc) / (nrenc - renc)
		else:
			trim = 100 # sort of infinite
		print ('trim: ' + str(trim))
		# start simple: if left is faster, make it a bit slower. Not sensitive to how much faster
		if (trim < 0.95):
			left_speed += 10
			if (left_speed > speed * 2):
				left_speed = speed * 2
			set_left_speed(left_speed)
			print('increasing left_speed to ' + str(left_speed))
		elif (trim > 1.05):
			left_speed -= 10
			if (left_speed < speed / 2):
				left_speed = speed / 2
			set_left_speed(left_speed)
			print('decreasing left_speed to ' + str(left_speed))
	lenc = nlenc
	renc = nrenc

print('stop')
stop()
