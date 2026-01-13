#!/usr/bin/env python3
# encoding: utf-8
# @data:2022/11/07
# @author:aiden
# 肌体控制
import os
import cv2
import time
import queue
import rospy
import threading
import numpy as np
import faulthandler
import mediapipe as mp
import sdk.fps as fps
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from ros_robot_controller.msg import BuzzerState, MotorsState, MotorState, PWMServoState, SetPWMServoState

faulthandler.enable()

mp_pose = mp.solutions.pose

LEFT_SHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER
LEFT_ELBOW = mp_pose.PoseLandmark.LEFT_ELBOW
LEFT_WRIST = mp_pose.PoseLandmark.LEFT_WRIST
LEFT_HIP = mp_pose.PoseLandmark.LEFT_HIP

RIGHT_SHOULDER = mp_pose.PoseLandmark.RIGHT_SHOULDER
RIGHT_ELBOW = mp_pose.PoseLandmark.RIGHT_ELBOW
RIGHT_WRIST = mp_pose.PoseLandmark.RIGHT_WRIST
RIGHT_HIP = mp_pose.PoseLandmark.RIGHT_HIP

LEFT_KNEE = mp_pose.PoseLandmark.LEFT_KNEE
LEFT_ANKLE = mp_pose.PoseLandmark.LEFT_ANKLE

RIGHT_KNEE = mp_pose.PoseLandmark.RIGHT_KNEE
RIGHT_ANKLE = mp_pose.PoseLandmark.RIGHT_ANKLE

def get_joint_landmarks(img, landmarks):
    """
    将landmarks从medipipe的归一化输出转为像素坐标(Convert landmarks from medipipe's normalized output to pixel coordinates)
    :param img: 像素坐标对应的图片(picture corresponding to pixel coordinate)
    :param landmarks: 归一化的关键点(normalized keypoint)
    :return:
    """
    h, w, _ = img.shape
    landmarks = [(lm.x * w, lm.y * h) for lm in landmarks]
    return np.array(landmarks)

def joint_distance(landmarks):
    distance_list = []

    d1 = landmarks[LEFT_HIP] - landmarks[LEFT_SHOULDER]
    d2 = landmarks[LEFT_HIP] - landmarks[LEFT_WRIST]
    dis1 = d1[0]**2 + d1[1]**2
    dis2 = d2[0]**2 + d2[1]**2
    distance_list.append(round(dis1/dis2, 1))
   
    d1 = landmarks[RIGHT_HIP] - landmarks[RIGHT_SHOULDER]
    d2 = landmarks[RIGHT_HIP] - landmarks[RIGHT_WRIST]
    dis1 = d1[0]**2 + d1[1]**2
    dis2 = d2[0]**2 + d2[1]**2
    distance_list.append(round(dis1/dis2, 1))
    
    d1 = landmarks[LEFT_HIP] - landmarks[LEFT_ANKLE]
    d2 = landmarks[LEFT_ANKLE] - landmarks[LEFT_KNEE]
    dis1 = d1[0]**2 + d1[1]**2
    dis2 = d2[0]**2 + d2[1]**2
    distance_list.append(round(dis1/dis2, 1))
   
    d1 = landmarks[RIGHT_HIP] - landmarks[RIGHT_ANKLE]
    d2 = landmarks[RIGHT_ANKLE] - landmarks[RIGHT_KNEE]
    dis1 = d1[0]**2 + d1[1]**2
    dis2 = d2[0]**2 + d2[1]**2
    distance_list.append(round(dis1/dis2, 1))
    
    return distance_list

class BodyControlNode:
    def __init__(self, name):
        rospy.init_node(name)
        self.name = name
        self.drawing = mp.solutions.drawing_utils
        self.body_detector = mp_pose.Pose(
            static_image_mode=False,
            min_tracking_confidence=0.5,
            min_detection_confidence=0.5)
        
        self.image_queue = queue.Queue(maxsize=1)
        self.fps = fps.FPS()  # fps计算器
        
        self.running = True
        self.move_finish = True
        self.stop_flag = False
        self.left_hand_count = []
        self.right_hand_count = []
        self.left_leg_count = []
        self.right_leg_count = []

        self.detect_status = [0, 0, 0, 0]
        self.move_status = [0, 0, 0, 0]
        self.last_status = 0
        
        self.machine_type = os.environ.get('MACHINE_TYPE')
        self.camera_type = os.environ.get('DEPTH_CAMERA_TYPE')
        camera = rospy.get_param('/depth_camera/camera_name', 'depth_cam')
        self.image_sub = rospy.Subscriber('/%s/rgb/image_raw' % camera, Image, self.image_callback, queue_size=1)
        self.mecanum_pub = rospy.Publisher('/controller/cmd_vel', Twist, queue_size=1)
        self.buzzer_pub = rospy.Publisher('/ros_robot_controller/set_buzzer', BuzzerState, queue_size=1)
        self.motor_pub = rospy.Publisher('/ros_robot_controller/set_motor', MotorsState, queue_size=1)
        self.servo_state_pub = rospy.Publisher('ros_robot_controller/pwm_servo/set_state', SetPWMServoState, queue_size=1)
        time.sleep(0.2)
        self.mecanum_pub.publish(Twist())
        rospy.set_param('~init_finish', True)
        # twist = Twist()
        # twist.angular.z = -1
        # self.move(twist)
        self.image_proc()

    def image_callback(self, ros_image):
        bgr_image = np.ndarray(shape=(ros_image.height, ros_image.width, 3), dtype=np.uint8, buffer=ros_image.data)  # 将自定义图像消息转化为图像
        if not self.image_queue.empty():
            try:
                self.image_queue.get_nowait()
            except queue.Empty:
                pass
        try:
            self.image_queue.put_nowait(bgr_image)
        except queue.Full:
            pass

    def move(self, *args):
        if args[0].angular.z == 1:
            servo_state = PWMServoState()
            servo_state.id = [1]
            servo_state.position = [1200]
            data = SetPWMServoState()
            data.state = [servo_state]
            data.duration = 0.1
            self.servo_state_pub.publish(data)
            time.sleep(0.2)
            motor1 = MotorState()
            motor1.id = 2
            motor1.rps = 0.1
            motor2 = MotorState()
            motor2.id = 4
            motor2.rps = -2
            self.motor_pub.publish([motor1, motor2])
            time.sleep(7)
            servo_state = PWMServoState()
            servo_state.id = [1]
            servo_state.position = [1500]
            data = SetPWMServoState()
            data.state = [servo_state]
            data.duration = 0.1
            self.servo_state_pub.publish(data)
            motor1 = MotorState()
            motor1.id = 2
            motor1.rps = 0
            motor2 = MotorState()
            motor2.id = 4
            motor2.rps = 0
            self.motor_pub.publish([motor1, motor2])
        elif args[0].angular.z == -1:
            servo_state = PWMServoState()
            servo_state.id = [1]
            servo_state.position = [1850]
            data = SetPWMServoState()
            data.state = [servo_state]
            data.duration = 0.1
            self.servo_state_pub.publish(data)
            time.sleep(0.2)
            motor1 = MotorState()
            motor1.id = 2
            motor1.rps = 2
            motor2 = MotorState()
            motor2.id = 4
            motor2.rps = -0.1
            self.motor_pub.publish([motor1, motor2])
            time.sleep(8)
            servo_state = PWMServoState()
            servo_state.id = [1]
            servo_state.position = [1500]
            data = SetPWMServoState()
            data.state = [servo_state]
            data.duration = 0.1
            self.servo_state_pub.publish(data)
            motor1 = MotorState()
            motor1.id = 2
            motor1.rps = 0
            motor2 = MotorState()
            motor2.id = 4
            motor2.rps = 0
            self.motor_pub.publish([motor1, motor2])
        else:
            self.mecanum_pub.publish(args[0])
            time.sleep(args[1])
            self.mecanum_pub.publish(Twist())
            time.sleep(0.1)
        self.stop_flag =True
        self.move_finish = True

    def buzzer_warn(self):
        msg = BuzzerState()
        msg.freq = 2000
        msg.on_time = 0.2
        msg.off_time = 0.01
        msg.repeat = 1
        self.buzzer_pub.publish(msg)

    def image_proc(self):
        while self.running:
            image = self.image_queue.get(block=True)
            result_image = image.copy()
            results = self.body_detector.process(image)
            if results is not None and results.pose_landmarks is not None:
                if self.move_finish:
                    twist = Twist()
                    landmarks = get_joint_landmarks(image, results.pose_landmarks.landmark)
                    distance_list = (joint_distance(landmarks))
                  
                    if distance_list[0] < 1:
                        self.detect_status[0] = 1
                    if distance_list[1] < 1:
                        self.detect_status[1] = 1
                    if 0 < distance_list[2] < 2:
                        self.detect_status[2] = 1
                    if 0 < distance_list[3] < 2:
                        self.detect_status[3] = 1
                    
                    self.left_hand_count.append(self.detect_status[0])
                    self.right_hand_count.append(self.detect_status[1])
                    self.left_leg_count.append(self.detect_status[2])
                    self.right_leg_count.append(self.detect_status[3])                   
                    #print(distance_list) 
                   
                    if len(self.left_hand_count) == 4:
                        count = [sum(self.left_hand_count), 
                                 sum(self.right_hand_count), 
                                 sum(self.left_leg_count), 
                                 sum(self.right_leg_count)]

                        self.left_hand_count = []
                        self.right_hand_count = []
                        self.left_leg_count = []
                        self.right_leg_count = []
                    
                        if self.stop_flag:
                            if count[self.last_status - 1] <= 1:
                                self.stop_flag = False
                                self.move_status = [0, 0, 0, 0]
                                self.buzzer_warn()
                        else:
                            if count[0] > 2:
                                self.move_status[0] = 1
                            if count[1] > 2:
                                self.move_status[1] = 1
                            if count[2] > 2:
                                self.move_status[2] = 1
                            if count[3] > 2:
                                self.move_status[3] = 1

                            if self.move_status[0]:
                                self.move_finish = False
                                self.last_status = 1
                                if self.machine_type == 'ROSOrin_Mecanum':
                                    twist.linear.y = -0.3
                                elif self.machine_type == 'ROSOrin_Acker':
                                    twist.angular.z = -1
                                elif self.machine_type == 'ROSOrin_Differential':
                                    twist.linear.x = -0.3
                                threading.Thread(target=self.move, args=(twist, 1)).start()
                            elif self.move_status[1]:
                                self.move_finish = False
                                self.last_status = 2
                                if self.machine_type == 'ROSOrin_Mecanum':
                                    twist.linear.y = 0.3
                                elif self.machine_type == 'ROSOrin_Acker':
                                    twist.angular.z = 1
                                elif self.machine_type == 'ROSOrin_Differential':
                                    twist.linear.x = 0.3
                                threading.Thread(target=self.move, args=(twist, 1)).start()
                            elif self.move_status[2]:
                                self.move_finish = False
                                self.last_status = 3
                                twist.linear.x = 0.3
                                threading.Thread(target=self.move, args=(twist, 1)).start()
                            elif self.move_status[3]:
                                self.move_finish = False
                                self.last_status = 4
                                twist.linear.x = -0.3
                                threading.Thread(target=self.move, args=(twist, 1)).start()

                    self.detect_status = [0, 0, 0, 0]
                
                self.drawing.draw_landmarks(
                    result_image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS)
            
            self.fps.update()
            result_image = self.fps.show_fps(cv2.flip(result_image, 1))
            result_image = cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR) if self.camera_type == 'usb_cam' else result_image
            cv2.imshow(self.name, result_image)
            key = cv2.waitKey(1)
            if key != -1:
                self.mecanum_pub.publish(Twist())
                self.running = False

if __name__ == "__main__":
    print('\n******Press any key to exit!******')
    BodyControlNode('body_control')
