#!/usr/bin/env python

# Tello Python3 Control Demo 
#
# http://www.ryzerobotics.com/
#
# 1/1/2018

# This is a Server. TELLO has its own client.
# Type the commands, and it will send the UDP Packets to the UDP CLients.
# Problem to solve: Once ctrl-c from Track, you cannot type track again and go to Tracking

import threading 
import socket
import sys
import time
import platform  

# Python libs

import math
import random
import actionlib
import subprocess
import signal

# numpy and scipy
import numpy as np


# Ros libraries
import roslib
import rospy

# Ros Messages

from geometry_msgs.msg import Twist, Point, Pose
from std_msgs.msg import Empty
from std_msgs.msg import String
from std_msgs.msg import Float64
from nav_msgs.msg import Odometry
from unity_robotics_demo_msgs.msg import PosRot
from unity_robotics_demo_msgs.msg import QRPose


def recv():
    count = 0
    global feedback
    while True: 
        try:
            data, server = sock.recvfrom(1518)
	    feedback = data.decode(encoding="utf-8")
            #print(data.decode(encoding="utf-8"))
	    print (feedback)
        except Exception:
            print ('\nExit . . .\n')
            break


def cubePos(currentcubePos):
    global cube
    cube.position.x = -currentcubePos.pos_z
    cube.position.y = currentcubePos.pos_x
    cube.position.z = currentcubePos.pos_y

def telloPos(currenttelloPos):
    global tello
    tello.position.x = -currenttelloPos.QR_pos_z
    tello.position.y = currenttelloPos.QR_pos_x
    tello.position.z = currenttelloPos.QR_pos_y

def userInput():
	global feedback
	feedback = ''

	while True: 
	    try:
		python_version = str(platform.python_version())
		version_init_num = int(python_version.partition('.')[0]) 
	        print ('Type the commands to send to Tello\n')
		if version_init_num == 3:
		    msg = input("");
		elif version_init_num == 2:
		    msg = raw_input("");
		
		if not msg:
		    break  

		if 'track' in msg:
		    print ('...')
		    #sock.close() 
		    break

		if 'stop' in msg:
		    print ('...')
		    #sock.close() 
		    break

		# Send data
		msg = msg.encode(encoding="utf-8") 
		sent = sock.sendto(msg, tello_address)
		print("Msg sent: ", msg)
		#while('ok' not in feedback):
			

	    except KeyboardInterrupt:
		print ('\n . . .\n')
		#sock.close()  
		break
	return msg

def trackCube():
# Sending go to commands to the Tello
	global feedback
	telloPose = Pose()
	cubePose = Pose()
	feedback = ''

	while(not rospy.is_shutdown()):
	    try:
		cubePose = cube
		telloPose = tello
		print("Cube x: ", cubePose.position.x, " Cube y: ", cubePose.position.y)
		print("Tello x: ", telloPose.position.x, " Tello y: ", telloPose.position.y, " Tello z: ", telloPose.position.z)
		goalPose.position.x = 100*(cubePose.position.x - telloPose.position.x)
		goalPose.position.y = 100*(cubePose.position.y - telloPose.position.y)
		goalPose.position.z = 100*(cubePose.position.z - telloPose.position.z)
		print("Goal x: ", goalPose.position.x, " Goal y: ", goalPose.position.y, " Goal z: ", goalPose.position.z)
		
		if(telloPose):

			# For Forward and Backward

			if (goalPose.position.x < 0):

				msg = "back " + str(abs(goalPose.position.x))

			else:
				msg = "forward " + str(abs(goalPose.position.x))

			print("I updated msg")


			msg = msg.encode(encoding="utf-8")
			feedback = ''

			sent = sock.sendto(msg, tello_address)
			print("Msg sent: ", msg)

			print 'Waiting for feedback'
			
			while(feedback=='' and not rospy.is_shutdown()):
				if ('error' in feedback):
					break
				if ('out of range' in feedback):
					break

			# Now for Left - Right

			if (goalPose.position.y < 0):

				msg = "right " + str(abs(goalPose.position.y))

			else:
				msg = "left " + str(abs(goalPose.position.y))

			print("I updated msg")


			msg = msg.encode(encoding="utf-8")
			feedback = ''

			sent = sock.sendto(msg, tello_address)
			print("Msg sent: ", msg)

			print 'Waiting for feedback'
			
			while(feedback=='' and not rospy.is_shutdown()):
				if ('error' in feedback):
					break
				if ('out of range' in feedback):
					break

			# Now for Up - Down

			if (goalPose.position.z < 0):

				msg = "down " + str(abs(goalPose.position.z))

			else:
				msg = "up " + str(abs(goalPose.position.z))

			print("I updated msg")


			msg = msg.encode(encoding="utf-8")
			feedback = ''

			sent = sock.sendto(msg, tello_address)
			print("Msg sent: ", msg)

			print 'Waiting for feedback'
			
			while(feedback=='' and not rospy.is_shutdown()):
				if ('error' in feedback):
					break
				if ('out of range' in feedback):
					break

		
	    except KeyboardInterrupt:
		print ('\n . . .\n')
		#sock.close() 
		check = False 
		break


def main():

	rospy.init_node('Tello_Server')

	global cube, tello, sock, tello_address, goalPose, feedback
	cube = Pose()
	tello = Pose()
	goalPose = Pose()
	
	sub_cube = rospy.Subscriber("/pos_rot", PosRot, cubePos)
	sub_tello = rospy.Subscriber("/qr_code_pose", QRPose, telloPos)

	host = ''
	port = 9000
	locaddr = (host,port) 


	# Create a UDP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	#tello_address = ('192.168.10.1', 8889)
	tello_address = ('172.20.10.5', 8889) 
	sock.bind(locaddr)


	print ('\r\n\r\nTello Python3 Demo.\r\n')

	print ('Tello: command takeoff land flip forward back left right \r\n       up down cw ccw speed speed?\r\n')

	print ('end -- quit demo.\r\n')


	#recvThread create
	recvThread = threading.Thread(target=recv)
	recvThread.start()

	msg = ""

	while(not 'stop' in msg):
		msg = userInput()

		if('track' in msg):
			trackCube()
	
	msg = "go 0 0 0 1"
	# Send data
	msg = msg.encode(encoding="utf-8") 
	sent = sock.sendto(msg, tello_address)
	print("Msg sent: ", msg)

	#msg = "land"
	# Send data
	#msg = msg.encode(encoding="utf-8") 
	#sent = sock.sendto(msg, tello_address)
	#print("Msg sent: ", msg)

	python_version = str(platform.python_version())
	version_init_num = int(python_version.partition('.')[0]) 
        print ('Type land to land and turn-off the Tello\n')

	if version_init_num == 3:
	    msg = input("");
	elif version_init_num == 2:
	    msg = raw_input("");

	# Send data
	msg = msg.encode(encoding="utf-8") 
	sent = sock.sendto(msg, tello_address)
	print("Msg sent: ", msg)
	sock.close()
	
	rospy.spin()


if __name__ == '__main__':
    main()


