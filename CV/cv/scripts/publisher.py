#!/usr/bin/env python3

import rospy
from std_msgs.msg import Int32
from std_msgs.msg import String
import json
import time
import sys
import os
import subprocess

class FloorPublisher:
        def __init__(self):
                cv_command = "python3 /home/pi/hcrcv/yolo-qr/main.py"
                subprocess.Popen(cv_command, shell=True)
                rospy.init_node('floor_publisher')
                self.floor_pub = rospy.Publisher('/current_floor', Int32, queue_size=10)
                self.detections_pub = rospy.Publisher('/cv_detections', String, queue_size=10)
                self.rate = rospy.Rate(0.5) # publish once per two second
                self.file_path = "/home/pi/hcrcv/yolo-qr/hcrcv_detections.json" # replace with your own file path
                self.data = None
                self.previous_floor = None
                self.floor = 0
                self.run()

        def load_json_data(self):
                self.data = json.load(open(self.file_path))

        def is_valid_floor(self, raw_floor):
                return 'floor-' in raw_floor

        def strip_floor(self, raw_floor):
                return raw_floor.replace('floor-', '')

        def run(self):
                while not rospy.is_shutdown():
                        try:
                                if int(time.time()) % 5 == 0:
                                        print('Entered the pit')
                                        self.load_json_data()
                                        self.detections_pub.publish(str(self.data))
                                        raw_floor = str(self.data['floor'])
                                        print('Entered the pit 2')
                                        print(raw_floor)
                                        if self.is_valid_floor(raw_floor):
                                                print('Entered the pit 3')
                                                self.previous_floor = self.floor
                                                self.floor = self.strip_floor(raw_floor)
                                                print(self.floor)
                                                # os.system('python ~/catkin_ws/src/pepper-ros-navigation/src/pub_map.py '+ str(self.floor))
                                                #if self.previous_floor != self.floor:
                                                print('Entered the pit 4')
                                                self.floor_pub.publish(int(self.floor))
                                                rospy.loginfo(rospy.get_caller_id() + 'The current floor number %s \n', str(self.floor))
                                                print('Entered the pit 5')
                                        self.rate.sleep()
                        except Exception as e:
                                print(e)
                rospy.spin()

if __name__ == '__main__':
    try:
        floor_publisher = FloorPublisher()
    except rospy.ROSInterruptException:
        print("PEEPEEPOOPOO")
        pass
