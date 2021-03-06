#! /usr/bin/env python
##############################################################################################################                                                              
# This example is for streaming video and controlling the GoPiGo from a web browser
# http://www.dexterindustries.com/GoPiGo/                                                                
# History
# ------------------------------------------------
# Author     Date      		Comments
# Karan      24 July 14  	Initial Authoring         
# Karan		 19 Feb 15		Converted to 1 joystick mode                                                 
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)           
#
# This example is derived from the Dawn Robotics Raspberry Pi Camera Bot
# https://bitbucket.org/DawnRobotics/raspberry_pi_camera_bot
#############################################################################################################

# Copyright (c) 2014, Dawn Robotics Ltd
# All rights reserved.

# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, 
# this list of conditions and the following disclaimer in the documentation 
# and/or other materials provided with the distribution.

# 3. Neither the name of the Dawn Robotics Ltd nor the names of its contributors 
# may be used to endorse or promote products derived from this software without 
# specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging
import math
import time
import Queue
import threading
import gopigo
from rcontrol import * # my  encoder controlled robot controller

#--------------------------------------------------------------------------------------------------- 
debug=0
class RobotController:
  
    MAX_UPDATE_TIME_DIFF = 0.25
    TIME_BETWEEN_SERVO_SETTING_UPDATES = 1.0
    
    JOYSTICK_DEAD_ZONE = 0.1
    
    MOTION_COMMAND_TIMEOUT = 2.0 # If no commands for the motors are recieved in this time then
                                 # the motors (drive and servo) are set to zero speed
    speed_l=200
    speed_r=200
    #-----------------------------------------------------------------------------------------------
    def __init__( self ):
        gopigo.set_speed(200)
        gopigo.stop()
        #gopigo.fwd()
        
        self.lastServoSettingsSendTime = 0.0
        self.lastUpdateTime = 0.0
        self.lastMotionCommandTime = time.time()
        self.last_heading = 0
        self.m = Move()
    
    #-----------------------------------------------------------------------------------------------
    def __del__( self ):
        
        self.disconnect()
    
    #-----------------------------------------------------------------------------------------------
    def disconnect( self ):
        print "Closing"
       
    def normaliseJoystickData( self, joystickX, joystickY ):
        stickVectorLength = math.sqrt( joystickX**2 + joystickY**2 )
        if stickVectorLength > 1.0:
            joystickX /= stickVectorLength
            joystickY /= stickVectorLength
        
        if stickVectorLength < self.JOYSTICK_DEAD_ZONE:
            joystickX = 0.0
            joystickY = 0.0
            
        return ( joystickX, joystickY )

    def centreNeck( self ):
        #gopigo.set_right_speed(0)
		pass
       
    def setMotorJoystickPos( self, joystickX, joystickY ):
        joystickX, joystickY = self.normaliseJoystickData( joystickX, joystickY )
        if debug:
			print "Left joy",joystickX, joystickY
			#print self.speed_l*joystickY
        #gopigo.set_left_speed(int(self.speed_l*joystickY))
        #gopigo.fwd()
        if joystickX > .5:
            if self.last_heading != 2.0:
                self.m.move(heading = 2.0)
                self.last_heading = 2.0
                print "Right"
            #gopigo.left()
        elif joystickX <-.5:
            if self.last_heading != 0.5:
                print "Left"
                self.m.move(heading = 0.5)
                self.last_heading = 0.5
	    #gopigo.right()
        elif joystickY > .5:
            if self.last_heading != 1:
                print "Fwd"
                self.m.move(heading = 1)
                self.last_heading = 1
			#gopigo.fwd()
        elif joystickY < -.5:
			print "Back"
			#gopigo.bwd()
        else:
            if self.last_heading != 0:
                print "Stop"
                self.m.stop()
                self.last_heading = 0
			#gopigo.stop()
		
    def setNeckJoystickPos( self, joystickX, joystickY ):
        #print "g"
        joystickX, joystickY = self.normaliseJoystickData( joystickX, joystickY )
        if debug:	
			print "Right joy",joystickX, joystickY
			#print self.speed_r*joystickY
        #gopigo.set_right_speed(int(self.speed_r*joystickY))
        #gopigo.fwd()
        #self.lastMotionCommandTime = time.time()

    def update( self ):
        if debug:	
			print "Updating"
        curTime = time.time()
        timeDiff = min( curTime - self.lastUpdateTime, self.MAX_UPDATE_TIME_DIFF )
        self.m.course_correct()
        # Turn off the motors if we haven't received a motion command for a while
        #if curTime - self.lastMotionCommandTime > self.MOTION_COMMAND_TIMEOUT:
		#	self.leftMotorSpeed = 0.0
		#	self.rightMotorSpeed = 0.0
		#	self.panSpeed = 0.0
		#	self.tiltSpeed = 0.0

        self.lastUpdateTime = curTime
