#!/usr/bin/env python
#############################################################################################################                                                                  
# Rafi: Trying to move forward while reading the encoders and correcting for bias
##############################################################################################################

from gopigo import *	#Has the basic functions for controlling the GoPiGo Robot
import signal

def signalHandler(signum, frame):
	if signum in [signal.SIGINT, signal.SIGTERM]:
		global stop_now
		stop_now = True


class Move(object):
	def __init__(self, calibrate = 0.8):
		self.lenc = enc_read(0)
		self.renc = enc_read(1)
		self.speed = 100
		self.calibrate = calibrate
		self.left_speed = int(self.speed * self.calibrate)
		self.heading = 1.0
		stop()
		self.lenc = enc_read(0)
		self.renc = enc_read(1)
		set_speed(self.speed)
		set_left_speed(self.left_speed)

	def move(self, heading = 1.0, speed = 100):
		self.heading = heading
		self.speed = speed
		self.left_speed = int(self.speed * self.calibrate * self.heading)
		self.lenc = enc_read(0)
		self.renc = enc_read(1)
		set_speed(self.speed)
		set_left_speed(self.left_speed)
		motor_fwd()
		set_speed(self.speed)
		set_left_speed(self.left_speed)

	def course_correct(self):
		nlenc = enc_read(0)
		nrenc = enc_read(1)
		print('left: ' + str(nlenc - self.lenc) + ' right: ' + str(nrenc - self.renc))
		if (nlenc != -1) and (self.lenc != -1) and (nrenc != -1) and (self.renc != -1): # all reading are valid
			if (nrenc > self.renc): # right wheel moved at all?
				trim = float(nlenc - self.lenc) / (nrenc - self.renc)
			else:
				trim = 100 # sort of infinite
			print ('trim: ' + str(trim))
			if (trim < 0.95 * self.heading):
				self.left_speed += 10
				if (self.left_speed > self.speed * 2 * self.heading):
					self.left_speed = int(self.speed * 2 * self.heading)
				set_left_speed(self.left_speed)
				print ('increasing left speed to ' + str(self.left_speed))
			elif (trim > 1.05 * self.heading):
				self.left_speed -= 10
				if (self.left_speed < self.speed * self.heading / 2):
					self.left_speed = int( self.left_speed * self.heading / 2)
				set_left_speed(self.left_speed)
				print ('reducing left speed to ' + str(self.left_speed))
		self.lenc = nlenc
		self.renc = nrenc
		


stop_now = False
signal.signal(signal.SIGINT, signalHandler)
signal.signal(signal.SIGTERM, signalHandler)

m = Move()
m.move(heading = 1.0)
while not stop_now:
	time.sleep(0.1)
	m.course_correct()

print('stop')
stop()
