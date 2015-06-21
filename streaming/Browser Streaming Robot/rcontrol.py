#!/usr/bin/env python
#############################################################################################################                                                                  
# Rafi: Trying to move forward while reading the encoders and correcting for bias
# Should improve by treating left and right more equally
##############################################################################################################

from gopigo import *	#Has the basic functions for controlling the GoPiGo Robot
import signal
from kbhit import KBHit

def signalHandler(signum, frame):
	if signum in [signal.SIGINT, signal.SIGTERM]:
		global stop_now
		stop_now = True


class Move(object):
	def __init__(self, calibrate = 0.8):
		self.lenc = enc_read(0)
		self.renc = enc_read(1)
		self.speed = 0
		self.calibrate = calibrate
		self.right_speed = 0
		self.left_speed = 0
		self.heading = 1.0
		stop()
		self.lenc = enc_read(0)
		self.renc = enc_read(1)

	def stop(self):
		self.speed = 0
		stop()

	def move(self, heading = 1.0, speed = 100):
		print('move in direction ' + str(heading))
		self.heading = heading
		self.speed = speed
		self.left_speed = int(self.speed * self.calibrate * self.heading)
		self.right_speed = self.speed
		self.lenc = enc_read(0)
		self.renc = enc_read(1)
		motor_fwd()
		#set_speed(self.speed)
		set_left_speed(self.left_speed)
		set_right_speed(self.right_speed)

	def veer_right(self, amount):
		if ( (self.left_speed + amount) <= self.speed):
			self.left_speed += amount
			set_left_speed(self.left_speed)
			print ('veer right by increasing left speed by ' + str(amount) + ' to ' + str(self.left_speed))
		elif (self.right_speed >= amount):
			self.right_speed -= amount
			set_right_speed(self.right_speed)
			print ('veer right by decreasing right speed by ' + str(amount) + ' to ' + str(self.right_speed))
		else:
			print ('could not veer right')

	def veer_left(self, amount):
		if ( (self.right_speed + amount) < self.speed):
			self.right_speed += amount
			set_right_speed(self.right_speed)
			print ('veer left by increasing right speed by ' + str(amount) + ' to ' + str(self.right_speed))
		elif (self.left_speed > amount):
			self.left_speed -= amount
			set_left_speed(self.left_speed)
			print ('veer left by decreasing left speed by ' + str(amount) + ' to ' + str(self.left_speed))
		else:
			print ('could not veer left')


	def course_correct(self):
		if self.speed == 0:
			return
		
		nlenc = enc_read(0)
		nrenc = enc_read(1)
		print('left: ' + str(nlenc - self.lenc) + ' right: ' + str(nrenc - self.renc))
		if ( (nlenc - self.lenc) == 0 and (nrenc - self.renc) == 0 ):
			# we should be moving but we're stopped, retry moving forward
			self.move(self.heading, self.speed)
			return
		
		if (nlenc != -1) and (self.lenc != -1) and (nrenc != -1) and (self.renc != -1): # all reading are valid
			if (nrenc > self.renc): # right wheel moved at all?
				trim = float(nlenc - self.lenc) / (nrenc - self.renc)
			else:
				trim = 100 # sort of infinite
			print ('trim: ' + str(trim))
			if (trim < 0.95 * self.heading):
				self.veer_right(10)
			elif (trim > 1.05 * self.heading):
				self.veer_left(10)
		self.lenc = nlenc
		self.renc = nrenc
		

if __name__ == '__main__' :
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
