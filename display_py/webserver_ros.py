#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from std_msgs.msg import Int32
from geometry_msgs.msg import PoseWithCovarianceStamped
import base64
import requests

def write_file(name, dataB64):
  requests.post("http://192.168.0.103:5550/"+name, dataB64)

def callback_floor(data):
  print("floor " + str(data.data))
#  bd = base64.b64encode(bytes(str(data), 'utf8'))
  bd = bytes(str(data.data), 'utf8')
  write_file("floor", bd)

def callback_say(data):
  print("say " + str(data.data))
#  bd = base64.b64encode(bytes(str(data), 'utf8'))
  bd = bytes(str(data.data), 'utf8')
  write_file("saying", bd)

def callback_pos(data):
  x = data.pose.pose.position.x
  y = data.pose.pose.position.y
  print("position " + str(x) + ";" + str(y))
#  bd = base64.b64encode(bytes(str(data), 'utf8'))
  bd = bytes(str(x) + ";" + str(y), 'utf8')
  write_file("position", bd)

rospy.init_node('webserver', anonymous=True)
rospy.Subscriber("current_floor", Int32, callback_floor)
rospy.Subscriber("speak", String, callback_say)
rospy.Subscriber("amcl_pose", PoseWithCovarianceStamped, callback_pos)
print("Ros Started")
rospy.spin()


