#!/usr/bin/env python3
# encoding: utf-8
# 手掌中心点追踪与发布 (使用自定义Point2D消息)
import os
import cv2
import rospy
import numpy as np
import faulthandler
import mediapipe as mp
import sdk.fps as fps
from sensor_msgs.msg import Image
from interfaces.msg import Point2D  
from std_srvs.srv import Trigger, TriggerResponse
from sdk.common import cv2_image2ros

faulthandler.enable()

def get_hand_landmarks(img, landmarks):
    """
    将landmarks从medipipe的归一化输出转为像素坐标
    :param img: 像素坐标对应的图片
    :param landmarks: 归一化的关键点
    :return: 像素坐标的numpy数组
    """
    h, w, _ = img.shape
    landmarks_pixel = [(lm.x * w, lm.y * h) for lm in landmarks]
    return np.array(landmarks_pixel)

class HandPalmTrackerNode:
    def __init__(self, name):
        rospy.init_node(name)
        self.name = name

        # 初始化 MediaPipe Hands
        self.drawing = mp.solutions.drawing_utils
        self.hand_detector = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5
        )

        self.start = False
        self.running = True
        self.image = None
        self.fps = fps.FPS()
        self.camera_type = os.environ.get('DEPTH_CAMERA_TYPE')

        # === ROS 接口 ===
        # 订阅摄像头图像
        camera = rospy.get_param('/depth_camera/camera_name', 'depth_cam')
        rospy.Subscriber('/%s/rgb/image_raw' % camera, Image, self.image_callback)

        # 发布处理后的图像结果（用于调试）
        self.result_publisher = rospy.Publisher('~image_result', Image, queue_size=1)
        

        self.center_publisher = rospy.Publisher('~center', Point2D, queue_size=1)

        # 控制节点启停的服务
        rospy.Service('~start', Trigger, self.start_srv_callback)
        rospy.Service('~stop', Trigger, self.stop_srv_callback)

        # 处理启动参数
        self.display = rospy.get_param('~enable_display', False)
        if rospy.get_param('~start', False):
            self.start_srv_callback(None)
        
        rospy.set_param('~init_finish', True)
        rospy.loginfo("init_finish")

        self.image_proc()

    def start_srv_callback(self, msg):
        self.start = True
        return TriggerResponse(success=True)

    def stop_srv_callback(self, msg):
        rospy.loginfo("停止手掌追踪.")
        self.start = False
        return TriggerResponse(success=True)

    def image_callback(self, ros_image):
        """接收图像消息并转换为OpenCV格式"""
        self.image = np.ndarray(shape=(ros_image.height, ros_image.width, 3), dtype=np.uint8, buffer=ros_image.data)

    def image_proc(self):
        """主处理循环"""
        while self.running and not rospy.is_shutdown():
            if self.image is None:
                rospy.sleep(0.01)
                continue

            image_bgr = self.image.copy()
            self.image = None

            if self.camera_type == 'usb_cam':
                image_bgr = cv2.cvtColor(image_bgr, cv2.COLOR_RGB2BGR)

            image_flipped = cv2.flip(image_bgr, 1)
            frame_height, frame_width, _ = image_flipped.shape

            if self.start:
                try:
                    image_rgb = cv2.cvtColor(image_flipped, cv2.COLOR_BGR2RGB)
                    results = self.hand_detector.process(image_rgb)
                    
                    point2d_msg = Point2D()

                    if results.multi_hand_landmarks:
                        hand_landmarks = results.multi_hand_landmarks[0]
                        self.drawing.draw_landmarks(
                            image_flipped,
                            hand_landmarks,
                            mp.solutions.hands.HAND_CONNECTIONS)
                        
                        landmarks_pixel = get_hand_landmarks(image_flipped, hand_landmarks.landmark)
                        palm_points = landmarks_pixel[[0, 5, 9, 13, 17], :]
                        center_point = np.mean(palm_points, axis=0)

                        # 填充消息
                        point2d_msg.width = frame_width
                        point2d_msg.height = frame_height
                        point2d_msg.x = int(center_point[0])
                        point2d_msg.y = int(center_point[1])

                        cv2.circle(image_flipped, (point2d_msg.x, point2d_msg.y), 10, (0, 255, 0), -1)
                    else:
                        point2d_msg.width = 0
                        point2d_msg.height = 0
                        point2d_msg.x = 0
                        point2d_msg.y = 0
                    
                    self.center_publisher.publish(point2d_msg)

                except Exception as e:
                    rospy.logerr(f"处理手部检测时出错: {e}")
            
            self.fps.update()
            result_image = self.fps.show_fps(image_flipped)
            
            self.result_publisher.publish(cv2_image2ros(result_image, self.name))

            if self.display:
                cv2.imshow(self.name, result_image)
                if cv2.waitKey(1) != -1:
                    self.running = False
                    break
        
        if self.display:
            cv2.destroyAllWindows()
        rospy.loginfo("节点关闭.")


if __name__ == "__main__":
    try:
        node_name = 'hand_palm_tracker'
        HandPalmTrackerNode(node_name)
    except rospy.ROSInterruptException:
        pass
