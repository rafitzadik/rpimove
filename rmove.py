#!/usr/bin/env python
#############################################################################################################                                                                  
# Rafi: Trying to move forward while reading the encoders and correcting for bias
##############################################################################################################

from gopigo import *	#Has the basic functions for controlling the GoPiGo Robot
import time

min_speed_adjustment_time = 0.5
speed_increment = 20

class Move(object):
	def __init__(self, calibrate = 0.85):
		self.speed = 0
		self.final_speed = 0
		self.calibrate = calibrate
		self.right_speed = 0
		self.left_speed = 0
		self.heading = 1.0
		self.last_speed_adjustment_time = 0
		stop()
		self.lenc = enc_read(0)
		self.renc = enc_read(1)

	def stop(self):
		self.speed = 0
		stop()

	def move(self, heading = 1.0, speed = 200):
		#print('move in direction ' + str(heading))
		self.heading = heading
		self.final_speed = speed
		self.speed = min(70, speed)
		print("self.speed: ", self.speed, "self.final_speed: ", self.final_speed)
		self.last_speed_adjustment_time = time.time()
		if (self.calibrate * self.heading >= 1):
			self.left_speed = self.speed
			self.right_speed = int(self.speed / (self.calibrate * self.heading))
		else:
			self.left_speed = int(self.speed * self.calibrate * self.heading)
			self.right_speed = self.speed
		self.lenc = enc_read(0)
		self.renc = enc_read(1)
		#print('setting left_speed to: ' + str(self.left_speed) + ' right_speed to: ' + str(self.right_speed))
		set_left_speed(self.left_speed)
		time.sleep(0.1)
		set_right_speed(self.right_speed)
		time.sleep(0.1) #make sure the motors got the speed command
		motor_fwd()

	def veer_right(self, amount):
		print("veer right", amount)
		if ( (self.left_speed + amount) <= self.speed):
			self.left_speed += amount
			set_left_speed(self.left_speed)
			#print ('veer right by increasing left speed by ' + str(amount) + ' to ' + str(self.left_speed))
		elif (self.right_speed >= amount):
			self.right_speed -= amount
			set_right_speed(self.right_speed)
			#print ('veer right by decreasing right speed by ' + str(amount) + ' to ' + str(self.right_speed))
		#else:
			#print ('could not veer right')

	# def veer_right(self,amount):
	# 	self.right_speed -= amount
	# 	set_right_speed(self.right_speed)
	# 	print ('veer right by decreasing right speed by ' + str(amount) + ' to ' + str(self.right_speed))

	def veer_left(self, amount):
		print("veer left", amount)
		if ( (self.right_speed + amount) < self.speed):
			self.right_speed += amount
			set_right_speed(self.right_speed)
			#print ('veer left by increasing right speed by ' + str(amount) + ' to ' + str(self.right_speed))
		elif (self.left_speed > amount):
			self.left_speed -= amount
			set_left_speed(self.left_speed)
			#print ('veer left by decreasing left speed by ' + str(amount) + ' to ' + str(self.left_speed))
		#else:
			#print ('could not veer left')


	def course_correct(self):
		if self.speed == 0:
			return
		
		#do we need to adjust speed?
		if (time.time() - self.last_speed_adjustment_time > min_speed_adjustment_time) and (self.speed + speed_increment < self.final_speed):
			#increase whichever is bigger by 10, the other proportinally
			if (self.left_speed > self.right_speed):
				self.left_speed += speed_increment
				self.right_speed += speed_increment*self.right_speed / self.left_speed
			else:
				self.right_speed += speed_increment
				self.left_speed += speed_increment*self.left_speed / self.right_speed
			print("adjust speed", self.left_speed, self.right_speed)
			self.speed += speed_increment
			set_left_speed(self.left_speed)
			time.sleep(0.1)
			set_right_speed(self.right_speed)
			time.sleep(0.1)
			self.last_speed_adjustment_time = time.time()

		#adjust left or right based on encoders
		nlenc = enc_read(0)
		nrenc = enc_read(1)
		#print('left: ' + str(nlenc - self.lenc) + ' right: ' + str(nrenc - self.renc))
		if ( (nlenc - self.lenc) == 0 and (nrenc - self.renc) == 0 ):
			# we should be moving but we're stopped, retry moving forward
			self.move(self.heading, self.final_speed)
			return
		
		if (nlenc != -1) and (self.lenc != -1) and (nrenc != -1) and (self.renc != -1): # all reading are valid
			rdiff = nrenc - self.renc
			ldiff = nlenc - self.lenc
			if (self.heading == 1 and abs(rdiff - ldiff) <= 1):
				#just continue
				#print("going straight and diff is close enough")
				pass
			elif self.heading == 1:
				if (nrenc > self.renc): # right wheel moved at all?
					trim = float(nlenc - self.lenc) / (nrenc - self.renc)
				else:
					trim = 100 # sort of infinite
				#print ('trim: ' + str(trim))
				if (trim < self.heading):
					self.veer_right(self.speed / 30) # at a speed of 100, veer of 3 works well
				elif (trim > self.heading):
					self.veer_left(self.speed / 30)
				self.lenc = nlenc
				self.renc = nrenc
			else:
				self.lenc = nlenc
				self.renc = nrenc
		else:
			self.lenc = nlenc
			self.renc = nrenc
		


