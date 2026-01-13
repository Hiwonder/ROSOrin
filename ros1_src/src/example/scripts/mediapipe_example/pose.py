#!/usr/bin/env python3
# encoding: utf-8
import os
import cv2
import rospy
import signal
import numpy as np
import mediapipe as mp
import sdk.fps as fps
from sensor_msgs.msg import Image

class PoseNode:
    def __init__(self, name):
        rospy.init_node(name)
        self.image = None
        self.running = True
        self.fps = fps.FPS()
        signal.signal(signal.SIGINT, self.shutdown)
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.camera_type = os.environ.get('DEPTH_CAMERA_TYPE')
        rospy.Subscriber('/depth_cam/rgb/image_raw', Image, self.image_callback)  # 摄像头订阅
        self.run()

    def shutdown(self, signum, frame):
        self.running = False

    def image_callback(self, ros_image):
        self.image = np.ndarray(shape=(ros_image.height, ros_image.width, 3), dtype=np.uint8, buffer=ros_image.data) # 原始 RGB 画面
    
    def run(self):
        with self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while self.running:
                if self.image is not None:
                    self.image.flags.writeable = False
                    image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                    results = pose.process(image)

                    image.flags.writeable = True
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    self.mp_drawing.draw_landmarks(
                        image,
                        results.pose_landmarks,
                        self.mp_pose.POSE_CONNECTIONS)
                    self.fps.update()
                    result_image = self.fps.show_fps(cv2.flip(image, 1))
                    result_image = cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR) if self.camera_type == 'usb_cam' else result_image
                    cv2.imshow('MediaPipe Pose', result_image)
                    key = cv2.waitKey(10)
                    if key != -1:
                        break
                else:
                    rospy.sleep(0.01)

if __name__ == '__main__':
    PoseNode('Pose')
