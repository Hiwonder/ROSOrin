#!/usr/bin/env python3
# encoding: utf-8
# @data:2022/11/19
# @author:aiden
# 手势控制
import os
import sys
import cv2
import math
import time
import rospy
import signal
import numpy as np
from interfaces.msg import Points
from geometry_msgs.msg import Twist
from ros_robot_controller.msg import BuzzerState, PWMServoState, SetPWMServoState


class HandGestureControlNode:
    def __init__(self, name):
        rospy.init_node(name, anonymous=True)
        self.image = None
        self.points = []
        self.running = True
        self.left_and_right = 0
        self.up_and_down = 0
        self.last_point = [0, 0]

        signal.signal(signal.SIGINT, self.shutdown)
        self.machine_type = os.environ.get('MACHINE_TYPE')
        self.camera_type = os.environ.get('DEPTH_CAMERA_TYPE')
        rospy.Subscriber('/hand_trajectory/points', Points, self.get_hand_points_callback)
        self.buzzer_pub = rospy.Publisher('/ros_robot_controller/set_buzzer', BuzzerState, queue_size=1)
        self.servo_state_pub = rospy.Publisher('ros_robot_controller/pwm_servo/set_state', SetPWMServoState, queue_size=1)
        self.mecanum_pub = rospy.Publisher('/controller/cmd_vel', Twist, queue_size=1)

        rospy.sleep(1)
        self.init_action()
        self.hand_gesture_control()
    

    def init_action(self):
        if 'Acker' in self.machine_type:
            servo_state = PWMServoState()
            servo_state.id = [1]
            servo_state.position = [1500]
            data = SetPWMServoState()
            data.state = [servo_state]
            data.duration = 0.1
            self.servo_state_pub.publish(data)
        else:
            pass
        print('Init Finish')


    def buzzer_warn(self):
        msg = BuzzerState()
        msg.freq = 2000
        msg.on_time = 0.2
        msg.off_time = 0.01
        msg.repeat = 1
        self.buzzer_pub.publish(msg)


    def shutdown(self, signum, frame):
        self.running = False
        rospy.loginfo('shutdown')

    def get_hand_points_callback(self, msg):
        points = []
        left_and_right = [0]
        up_and_down = [0]
        if len(msg.points) > 10:
            for i in msg.points:
                if int(i.x) - self.last_point[0] > 0:
                    left_and_right.append(1)
                else:
                    left_and_right.append(-1)
                if int(i.y) - self.last_point[1] > 0:
                    up_and_down.append(1)
                else:
                    up_and_down.append(-1)
                points.extend([(int(i.x), int(i.y))])
                self.last_point = [int(i.x), int(i.y)]
            self.left_and_right = sum(left_and_right)
            self.up_and_down = sum(up_and_down)
            self.points = np.array(points)


    def acker_turn(self,pulse):
        servo_state = PWMServoState()
        servo_state.id = [1]
        servo_state.position = [pulse]
        data = SetPWMServoState()
        data.state = [servo_state]
        data.duration = 0.1
        self.servo_state_pub.publish(data)


    def hand_gesture_control(self):
        while self.running:
            if self.points != []:
                line = cv2.fitLine(self.points, cv2.DIST_L2, 0, 0.01, 0.01)
                angle = int(abs(math.degrees(math.acos(line[0][0]))))
                print('>>>>>>', angle)
                twist = Twist()
                if 90 >= angle > 60:
                    if self.up_and_down > 0:
                        print('down')
                        twist.linear.x = 0.2
                    else:
                        print('up')
                        twist.linear.x = -0.2
                    rospy.sleep(0.3)
                    self.acker_turn(1500)
    
                elif 30 > angle >= 0:
                    if self.left_and_right > 0:
                        print('right')
                        if 'Acker' in self.machine_type:
                            self.acker_turn(1200)
                            twist.linear.x = 0.2
                        elif 'Mecanum' in self.machine_type:
                            twist.linear.y = -0.1
                        else:
                            twist.angular.z = 0.5
                    else:
                        print('left')
                        if 'Acker' in self.machine_type:
                            self.acker_turn(1850)
                            twist.linear.x = 0.2
                        elif 'Mecanum' in self.machine_type:
                            twist.linear.y = 0.1
                        else:
                            twist.angular.z = 0.5                        
                    rospy.sleep(0.3)
                self.stop_flag = True
                if self.stop_flag:
                    self.stop_flag = False
                    self.buzzer_warn()
                self.mecanum_pub.publish(twist)
                time.sleep(2)
                self.mecanum_pub.publish(Twist())
                self.points = []
            else:
                rospy.sleep(0.01)

        rospy.signal_shutdown('shutdown')

if __name__ == "__main__":
    HandGestureControlNode('hand_gesture_control')
