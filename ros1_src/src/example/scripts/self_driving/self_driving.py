#!/usr/bin/env python3
# encoding: utf-8
# @data:2023/03/28
# @author:aiden
# 无人驾驶
import os
import cv2
import math
import time
import rospy
import queue
import signal
import threading
import numpy as np
import lane_detect
import sdk.pid as pid
import sdk.misc as misc
from sensor_msgs.msg import Image
import geometry_msgs.msg as geo_msg
from app.common import Heart
from interfaces.msg import ObjectsInfo
from std_srvs.srv import SetBool, SetBoolRequest, SetBoolResponse
from std_srvs.srv import Trigger, TriggerRequest, TriggerResponse
from sdk.common import cv2_image2ros, colors, plot_one_box

class SelfDrivingNode:
    def __init__(self, name):
        rospy.init_node(name, anonymous=True)
        self.name = name
 
        self.running = True
        self.pid = pid.PID(0.01, 0.0, 0.0)
        self.param_init() 
        self.classes = ['go', 'right', 'park', 'red', 'green', 'crosswalk']

        self.lock = threading.RLock()
        self.image_queue = queue.Queue(maxsize=1)
        signal.signal(signal.SIGINT, self.shutdown)
        self.machine_type = os.environ.get('MACHINE_TYPE')
        self.camera_type = os.environ.get('DEPTH_CAMERA_TYPE')
        self.lane_detect = lane_detect.LaneDetector("yellow")
        self.mecanum_pub = rospy.Publisher('/controller/cmd_vel', geo_msg.Twist, queue_size=1)  # 底盘控制
        self.result_publisher = rospy.Publisher(self.name + '/image_result', Image, queue_size=1)  # 图像处理结果发布

        self.result_publisher = rospy.Publisher('~image_result', Image, queue_size=1)
        self.enter_srv = rospy.Service('~enter', Trigger, self.enter_srv_callback)
        self.exit_srv = rospy.Service('~exit', Trigger, self.exit_srv_callback)
        self.set_running_srv = rospy.Service('~set_running', SetBool, self.set_running_srv_callback)
        self.heart = Heart(self.name + '/heartbeat', 5, lambda _: self.exit_srv_callback(None))

        if not rospy.get_param('~only_line_follow', False):
            while not rospy.is_shutdown():
                try:
                    if rospy.get_param('/yolov5/init_finish'):
                        break
                except:
                    time.sleep(0.1)
            rospy.ServiceProxy('/yolov5/start', Trigger)()
        rospy.sleep(0.2)
        self.mecanum_pub.publish(geo_msg.Twist())
        # self.park_action()

        self.dispaly = False
        if rospy.get_param('~start', True):
            self.dispaly = True
            self.enter_srv_callback(None)
            self.set_running_srv_callback(SetBoolRequest(data=True))
        self.image_proc()

    def param_init(self):
        self.image = None
        self.start = False
        self.enter = False

        self.have_turn_right = False
        self.detect_turn_right = False
        self.detect_far_lane = False
        self.park_x = -1  # 停车标识的x像素坐标

        self.start_turn_time_stamp = 0
        self.count_turn = 0
        self.start_turn = False  # 开始转弯

        self.count_right = 0
        self.count_right_miss = 0
        self.turn_right = False  # 右转标志
       
        self.last_park_detect = False
        self.count_park = 0
        self.stop = False  # 停下标识
        self.start_park = False  # 开始泊车标识

        self.count_crosswalk = 0
        self.crosswalk_distance = 0  # 离斑马线距离
        self.crosswalk_length = 0.1 + 0.3  # 斑马线长度 + 车长

        self.start_slow_down = False  # 减速标识
        self.normal_speed = 0.15  # 正常前进速度
        self.slow_down_speed = 0.1  # 减速行驶的速度

        self.traffic_signs_status = None  # 记录红绿灯状态
        self.red_loss_count = 0

        self.object_sub = None
        self.image_sub = None
        self.objects_info = []

    def shutdown(self, signum, frame):  # ctrl+c关闭处理
        self.running = False
        rospy.loginfo('shutdown')

    def image_callback(self, ros_image):  # 目标检查回调
        bgr_image = np.ndarray(shape=(ros_image.height, ros_image.width, 3), dtype=np.uint8, buffer=ros_image.data)  # 将自定义图像消息转化为图像
        if self.camera_type == 'usb_cam':
            bgr_image = cv2.cvtColor(bgr_image, cv2.COLOR_RGB2BGR)
        if not self.image_queue.empty():
            try:
                self.image_queue.get_nowait()
            except queue.Empty:
                pass
        try:
            self.image_queue.put_nowait(bgr_image)
        except queue.Full:
            pass

    def enter_srv_callback(self, _):
        rospy.loginfo("self driving enter")
        with self.lock:
            self.start = False
            depth_camera = rospy.get_param('/depth_camera/camera_name', 'depth_cam')
            self.image_sub = rospy.Subscriber('/%s/rgb/image_raw' % depth_camera, Image, self.image_callback)  # 摄像头订阅
            self.object_sub = rospy.Subscriber('/yolov5/object_detect', ObjectsInfo, self.get_object_callback)
            self.mecanum_pub.publish(geo_msg.Twist())
            self.enter = True
        return TriggerResponse(success=True)

    def exit_srv_callback(self, _):
        rospy.loginfo("self driving exit")
        with self.lock:
            try:
                if self.image_sub is not None:
                    self.image_sub.unregister()
                if self.object_sub is not None:
                    self.object_sub.unregister()
            except Exception as e:
                rospy.logerr(str(e))
            self.mecanum_pub.publish(geo_msg.Twist())
        self.param_init()
        self.lane_detect.set_roi(((450, 480, 0, 320, 0.7), (390, 420, 0, 320, 0.2), (330, 360, 0, 320, 0.1)))
        return TriggerResponse(success=True)
    
    def set_running_srv_callback(self, req: SetBoolRequest):
        rospy.loginfo("set_running")
        with self.lock:
            self.start = req.data
            if not self.start:
                self.mecanum_pub.publish(geo_msg.Twist())
        return SetBoolResponse(success=req.data)
    
    # 泊车处理
    def park_action(self):
        if self.machine_type == 'ROSOrin_Mecanum':
            twist = geo_msg.Twist()
            twist.linear.y = -0.2
            self.mecanum_pub.publish(twist)
            time.sleep(0.46/0.2)
        elif self.machine_type == 'ROSOrin_Differential':
            twist = geo_msg.Twist()
            time.sleep(0.5)
            twist.angular.z = -1.0
            self.mecanum_pub.publish(twist)
            time.sleep(1.1)
            self.mecanum_pub.publish(geo_msg.Twist())
            twist = geo_msg.Twist()
            twist.linear.x = 0.2
            self.mecanum_pub.publish(twist)
            time.sleep(0.40/0.2)
            self.mecanum_pub.publish(geo_msg.Twist())
            twist = geo_msg.Twist()
            twist.angular.z = 1.0
            self.mecanum_pub.publish(twist)
            time.sleep(1.1)
        else:
            twist = geo_msg.Twist()
            twist.linear.x = 0.15
            twist.angular.z = twist.linear.x*math.tan(-0.55)/0.17706
            self.mecanum_pub.publish(twist)
            time.sleep(3)

            twist = geo_msg.Twist()
            twist.linear.x = 0.1
            twist.angular.z = twist.linear.x*math.tan(0.4)/0.17706
            self.mecanum_pub.publish(twist)
            time.sleep(4)

            twist = geo_msg.Twist()
            twist.linear.x = -0.15
            twist.angular.z = twist.linear.x*math.tan(-0.3)/0.17706
            self.mecanum_pub.publish(twist)
            time.sleep(2.5)

        self.mecanum_pub.publish(geo_msg.Twist())

    def image_proc(self):
        while self.running:
            if self.enter:
                time_start = time.time()
                image = self.image_queue.get(block=True)
                result_image = image.copy()
                if self.start:
                    h, w = image.shape[:2]

                    # 获取车道线的二值化图
                    binary_image = self.lane_detect.get_binary(image)
                    # cv2.imshow('bin_image', binary_image)
                    # 检测到斑马线,开启减速标志
                    if 400 < self.crosswalk_distance and not self.start_slow_down:  # 只有足够近时才开始减速
                        self.count_crosswalk += 1
                        if self.count_crosswalk == 3:  # 多次判断，防止误检测
                            self.count_crosswalk = 0
                            self.start_slow_down = True  # 减速标识
                            self.count_slow_down = time.time()  # 减速固定时间
                    else:  # 需要连续检测，否则重置
                        self.count_crosswalk = 0

                    twist = geo_msg.Twist()
                    # 减速行驶处理
                    if self.start_slow_down:
                        if self.traffic_signs_status == 'red':  # 如果遇到红灯就停车
                            self.mecanum_pub.publish(geo_msg.Twist())
                            self.stop = True
                        elif self.traffic_signs_status == 'green':  # 遇到绿灯，速度放缓
                            twist.linear.x = self.slow_down_speed
                            self.stop = False
                        elif not self.stop:  # 其他非停止的情况速度放缓， 同时计时，时间=斑马线的长度/行驶速度
                            twist.linear.x = self.slow_down_speed
                            if time.time() - self.count_slow_down > self.crosswalk_length/twist.linear.x:
                                self.start_slow_down = False
                    else:
                        twist.linear.x = self.normal_speed  # 直走正常速度
                    
                    # print(self.park_x, self.crosswalk_distance, self.start_park)
                    if 0 < self.park_x and 250 < self.crosswalk_distance:
                        twist.linear.x = self.slow_down_speed
                        if self.machine_type != 'ROSOrin_Acker':
                            if not self.start_park and 320 < self.crosswalk_distance:  # 离斑马线足够近时就开启停车
                                self.mecanum_pub.publish(geo_msg.Twist())
                                self.start_park = True
                                self.stop = True
                                threading.Thread(target=self.park_action).start()
                        else:
                            if not self.start_park and 270 < self.crosswalk_distance:  # 离斑马线足够近时就开启停车
                                self.mecanum_pub.publish(geo_msg.Twist())
                                self.start_park = True
                                self.stop = True
                                threading.Thread(target=self.park_action).start()
                    
                    # 右转及停车补线策略
                    if self.detect_turn_right:
                        if 430 < self.crosswalk_distance:
                            self.detect_turn_right = False
                            self.turn_right = True
                    # print(self.park_x, self.start_turn, self.count_go, self.turn_right)
                    if self.turn_right:
                        self.lane_detect.set_roi(((430, 460, 0, 320, 0.7), (370, 400, 0, 320, 0.2), (310, 340, 0, 320, 0.1)))
                        y = self.lane_detect.add_horizontal_line(binary_image)
                        if 0 < y < 400 :
                            roi = [(0, y), (w, y), (w, 0), (0, 0)]
                            cv2.fillPoly(binary_image, [np.array(roi)], [0, 0, 0])  # 将上面填充为黑色，防干扰
                            min_x = cv2.minMaxLoc(binary_image)[-1][0]
                            if self.machine_type != 'ROSOrin_Acker':
                                cv2.line(binary_image, (min_x, y - 60), (w, y -60 ), (255, 255, 255), 50)  # 画虚拟线来驱使转弯
                            else:
                                cv2.line(binary_image, (min_x, y + 0), (w, y + 0), (255, 255, 255), 30)
                            # cv2.imshow('bin_image',binary_image)

                            self.lane_detect.set_roi(((390, 420, 0, 320, 0.7), (330, 360, 0, 320, 0.2), (270, 300, 0, 320, 0.1)))
                    elif (0 < self.park_x or self.have_turn_right) and not self.start_turn:  # 检测到停车标识需要填补线，使其保持直走
                        if not self.detect_far_lane:
                            up, down, center = self.lane_detect.add_vertical_line_near(binary_image)
                            binary_image[:, :] = 0  # 全置黑，防止干扰
                            if 50 < center < 80:  # 当将要看不到车道线时切换到识别较远车道线
                                self.detect_far_lane = True
                        else:
                            up, down = self.lane_detect.add_vertical_line_far(binary_image)
                            binary_image[:, :] = 0
                        if up != down:
                            cv2.line(binary_image, up, down, (255, 255, 255), 20)  # 手动画车道线
                    result_image, lane_angle, lane_x= self.lane_detect(binary_image, image.copy())  # 在处理后的图上提取车道线中心
                    # 巡线处理
                    # print('x = ',lane_x)
                    # 循线处理
                    # print(x)
                    
                    # cv2.imshow('bin_image',binary_image)
                    if not self.stop:
                        # print(self.turn_right, lane_x)
                        if self.turn_right:
                            if lane_x > 150:
                                if self.count_turn == 1:
                                    self.lane_detect.set_roi(((450, 480, 0, 320, 0.7), (390, 420, 0, 320, 0.2), (330, 360, 0, 320, 0.1)))
                                self.count_turn += 1
                                if self.count_turn > 5 and not self.start_turn:  # 稳定转弯
                                    # print('5 count')
                                    self.start_turn = True
                                    self.turn_right = False
                                    self.count_turn = 0
                                    self.start_turn_time_stamp = time.time()
                                if self.machine_type != 'ROSOrin_Acker':
                                    twist.angular.z = -0.65  # 转弯速度
                                else:
                                    twist.angular.z = twist.linear.x*math.tan(-0.55)/0.17706  # 转弯速度
                            else:  # 直道由pid计算转弯修正
                                self.count_turn = 0
                                if time.time() - self.start_turn_time_stamp > 2 and self.start_turn:
                                    self.turn_right = False
                                    self.start_turn = False
                                    # print('2 s')
                                if not self.start_turn:
                                    self.pid.SetPoint = 80  # 在车道中间时线的坐标
                                    if abs(lane_x - 80) < 20:
                                        lane_x = 80
                                    self.pid.update(lane_x)
                                    if self.machine_type != 'ROSOrin_Acker':
                                        twist.angular.z = misc.set_range(self.pid.output, -0.1, 0.1)
                                    else:
                                        twist.angular.z = twist.linear.x*math.tan(misc.set_range(self.pid.output, -0.3, 0.3))/0.17706
                                else:
                                    if self.machine_type == 'ROSOrin_Acker':
                                        twist.angular.z = 0.1*math.tan(-0.55)/0.17706  # 转弯速度
                        else:
                            if lane_x > 150:
                                self.count_turn += 1
                                if self.count_turn > 5 and not self.start_turn:  # 稳定转弯
                                    self.start_turn = True
                                    self.count_turn = 0
                                    self.start_turn_time_stamp = time.time()
                                if self.machine_type != 'ROSOrin_Acker':
                                    twist.angular.z = -0.65  # 转弯速度
                                else:
                                    twist.angular.z = twist.linear.x*math.tan(-0.55)/0.17706  # 转弯速度
                            else:  # 直道由pid计算转弯修正
                                self.count_turn = 0
                                if time.time() - self.start_turn_time_stamp > 2 and self.start_turn:
                                    self.start_turn = False
                                if not self.start_turn:
                                    self.pid.SetPoint = 80  # 在车道中间时线的坐标
                                    if abs(lane_x - 80) < 20:
                                        lane_x = 80
                                    self.pid.update(lane_x)
                                    if self.machine_type != 'ROSOrin_Acker':
                                        twist.angular.z = misc.set_range(self.pid.output, -0.1, 0.1)
                                    else:
                                        twist.angular.z = twist.linear.x*math.tan(misc.set_range(self.pid.output, -0.55, 0.55))/0.17706
                                    # print(twist.angular.z)
                                else:
                                    if self.machine_type == 'ROSOrin_Acker':
                                        twist.angular.z = 0.1*math.tan(-0.55)/0.17706  # 转弯速度
                        self.mecanum_pub.publish(twist)
                        if not self.start:
                            self.mecanum_pub.publish(geo_msg.Twist())
                    else:
                        self.pid.clear()
                    if self.objects_info != []:
                        for i in self.objects_info:
                            box = i.box
                            class_name = i.class_name
                            cls_conf = i.score
                            cls_id = self.classes.index(class_name)
                            color = colors(cls_id, True)
                            plot_one_box(
                                box,
                                result_image,
                                color=color,
                                label="{}:{:.2f}".format(class_name, cls_conf),
                            )
                else:
                    time.sleep(0.01)

                if self.dispaly:
                    cv2.imshow('result', result_image)
                    key = cv2.waitKey(1)
                    if key != -1:
                        self.running = False

                self.result_publisher.publish(cv2_image2ros(result_image))
                time_d = 0.03 - (time.time() - time_start)
                if time_d > 0:
                    time.sleep(time_d)
            else:
                time.sleep(0.01)

        self.mecanum_pub.publish(geo_msg.Twist())

    # 获取目标检测结果
    def get_object_callback(self, msg):
        self.objects_info = msg.objects
        if self.objects_info == []:  # 没有识别到时重置变量
            self.traffic_signs_status = None
            self.crosswalk_distance = 0
        else:
            min_distance = 0
            self.last_park_detect = False
            for i in self.objects_info:
                class_name = i.class_name
                center = (int((i.box[0] + i.box[2])/2), int((i.box[1] + i.box[3])/2))
                
                if class_name == 'crosswalk':  
                    cross_flag = True
                    if center[1] > min_distance:  # 获取最近的人行道y轴像素坐标
                        min_distance = center[1]
                if class_name == 'right':  # 获取右转标识
                    if not self.turn_right:
                        self.count_right += 1
                        self.count_right_miss = 0
                        if self.count_right >= 1:  # 检测到多次就将右转标志至真
                            self.have_turn_right = True
                            self.detect_turn_right = True
                            self.count_right = 0
                if class_name == 'park' and not self.turn_right:  # 获取停车标识中心坐标
                    self.park_x = center[0]
                if class_name == 'red' or class_name == 'green':  # 获取红绿灯状态
                    self.traffic_signs_status = class_name
                cross_flag = False
            if not self.last_park_detect:
                self.count_park = 0
            self.crosswalk_distance = min_distance

if __name__ == "__main__":
    SelfDrivingNode('self_driving')
