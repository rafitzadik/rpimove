#!/usr/bin/env python
#############################################################################################################                                                                  
# Rafi: Trying to move forward while reading the encoders and correcting for bias
##############################################################################################################

from gopigo import *	#Has the basic functions for controlling the GoPiGo Robot

class Move(object):
	def __init__(self, calibrate = 0.8):
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
		if (self.calibrate * self.heading >= 1):
			self.left_speed = self.speed
			self.right_speed = int(self.speed / (self.calibrate * self.heading))
		else:
			self.left_speed = int(self.speed * self.calibrate * self.heading)
			self.right_speed = self.speed
		self.lenc = enc_read(0)
		self.renc = enc_read(1)
		print('setting left_speed to: ' + str(self.left_speed) + ' right_speed to: ' + str(self.right_speed))
		motor_fwd()
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

	# def veer_right(self,amount):
	# 	self.right_speed -= amount
	# 	set_right_speed(self.right_speed)
	# 	print ('veer right by decreasing right speed by ' + str(amount) + ' to ' + str(self.right_speed))

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
			rdiff = nrenc - self.renc
			ldiff = nlenc - self.lenc
			if (self.heading == 1 and abs(rdiff - ldiff) <= 1):
				#just continue
				print("going straight and diff is close enough")
			else:
				if (nrenc > self.renc): # right wheel moved at all?
					trim = float(nlenc - self.lenc) / (nrenc - self.renc)
				else:
					trim = 100 # sort of infinite
				print ('trim: ' + str(trim))
				if (trim < self.heading):
					self.veer_right(2)
				elif (trim > self.heading):
					self.veer_left(2)
				self.lenc = nlenc
				self.renc = nrenc
		else:
			self.lenc = nlenc
			self.renc = nrenc
		


