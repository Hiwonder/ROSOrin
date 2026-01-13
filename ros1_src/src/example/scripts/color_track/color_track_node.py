#!/usr/bin/env python3
# encoding: utf-8
# @data:2022/11/23
# @author:aiden
# 颜色跟踪
import os
import rospy
import signal
import sdk.pid as pid
import sdk.misc as misc
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from std_srvs.srv import Trigger, TriggerResponse
from interfaces.msg import ColorsInfo, ColorDetect
from interfaces.srv import SetColorDetectParam, SetString

class ColorTrackNode:
    def __init__(self, name):
        rospy.init_node(name)
        self.y_dis = 500
        self.center = None
        self.running = True
        self.start = False
        self.name = name

        self.pid_y = pid.PID(0.003, 0.0, 0.001)

        signal.signal(signal.SIGINT, self.shutdown)
        self.machine_type = os.environ.get('MACHINE_TYPE')
        self.camera_type = os.environ.get('DEPTH_CAMERA_TYPE')
        self.mecanum_pub = rospy.Publisher('/controller/cmd_vel', Twist, queue_size=1)  # 底盘控制
        self.mecanum_pub.publish(Twist())

        rospy.Subscriber('/color_detect/color_info', ColorsInfo, self.get_color_callback)
        
        rospy.Service('~start', Trigger, self.start_srv_callback)  # 进入玩法
        rospy.Service('~stop', Trigger, self.stop_srv_callback)  # 退出玩法
        rospy.Service('~set_color', SetString, self.set_color_srv_callback)  # 设置颜色


        rospy.sleep(0.2)
        self.init_action()

        if rospy.get_param('~start', True):
            self.start_srv_callback(None)
            self.set_color_srv_callback(String('red'))

        rospy.set_param('~init_finish', True)

        self.color_track()

    def shutdown(self, signum, frame):
        self.running = False
        rospy.loginfo('shutdown')

    def init_action(self):
        self.mecanum_pub.publish(Twist())

    def set_color_srv_callback(self, msg):
        rospy.loginfo("set_color")

        msg_red = ColorDetect()
        msg_red.color_name = msg.data
        msg_red.detect_type = 'circle'
        rospy.wait_for_service('/color_detect/set_param', timeout=5.0)
        res = rospy.ServiceProxy('/color_detect/set_param', SetColorDetectParam)([msg_red])
        if res.success and msg.data != '':
            print('start_track_' + msg_red.color_name)
        else:
            print('track_fail')

        return [True, 'set_color']

    def start_srv_callback(self, msg):
        rospy.loginfo("start color track")

        self.start = True

        return TriggerResponse(success=True)

    def stop_srv_callback(self, msg):
        rospy.loginfo('stop color track')

        self.start = False
        res = rospy.ServiceProxy('/color_detect/set_param', SetColorDetectParam)()
        if res.success:
            print('set color success')
        else:
            print('set color fail')

        return TriggerResponse(success=True)

    def get_color_callback(self, msg):
        if msg.data != []:
            if msg.data[0].radius > 10:
                self.center = msg.data[0]
            else:
                self.center = None 
        else:
            self.center = None

    def color_track(self):
        while self.running:
            if self.center is not None and self.start:
                self.pid_y.SetPoint = self.center.width/2 
                if abs(self.center.x - self.center.width/2) < 50:
                    self.center.x = self.center.width/2 
                self.pid_y.update(self.center.x)
                self.pid_y.output = self.pid_y.output * 0.6
                twist = Twist()
                twist.angular.z = misc.set_range(self.pid_y.output, -2, 2)
                self.mecanum_pub.publish(twist)
            else:
                self.mecanum_pub.publish(Twist())
                rospy.sleep(0.01)
        
        rospy.signal_shutdown('shutdown')

if __name__ == "__main__":
    ColorTrackNode('color_track')
