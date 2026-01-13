#!/usr/bin/env python3
# encoding: utf-8
# @data:2022/11/07
# @author:aiden
# 手跟随
import time
import rospy
import signal
import sdk.pid as pid
from geometry_msgs.msg import Twist
from interfaces.msg import Point2D

class HandTrackNode:
    def __init__(self, name):
        rospy.init_node(name)
        self.name = name
        self.image = None
        self.center = None
        self.running = True
        self.y_dis = 500

        self.pid_y = pid.PID(0.003, 0.0, 0.001)

        signal.signal(signal.SIGINT, self.shutdown)

        self.mecanum_pub = rospy.Publisher('/controller/cmd_vel', Twist, queue_size=1)  # 底盘控制

        rospy.Subscriber('/hand_detect/center', Point2D, self.get_hand_callback)

        rospy.sleep(0.2)
        self.init_action()
        rospy.set_param('~init_finish', True)

        self.hand_track() 

    def shutdown(self, signum, frame):
        self.running = False
        rospy.loginfo('shutdown')

    def init_action(self):


        self.mecanum_pub.publish(Twist())

    def get_hand_callback(self, msg):
        if msg.width != 0:
            self.center = msg
        else:
            self.center = None

    def hand_track(self):
        while self.running:
            if self.center is not None:
                self.pid_y.SetPoint = self.center.width/2 
                if abs(self.center.x - self.center.width/2) < 50:
                    self.center.x = self.center.width/2
                self.pid_y.update(self.center.x)
                self.pid_y.output = self.pid_y.output * 0.6 * -1.0

                twist = Twist()
                angular_z = self.pid_y.output
                angular_z = max(min(angular_z, 0.5), -0.5)
                twist.angular.z = angular_z

                # 发布控制指令  
                self.mecanum_pub.publish(twist)
                time.sleep(0.01)
            else:
                self.mecanum_pub.publish(Twist())
                time.sleep(0.01)
        self.init_action() 
        rospy.signal_shutdown('shutdown')

if __name__ == "__main__":
    HandTrackNode('hand_track')
