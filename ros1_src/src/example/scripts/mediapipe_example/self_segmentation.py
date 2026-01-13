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


BG_COLOR = (192, 192, 192) # gray


class PoseNode:
    def __init__(self, name):
        rospy.init_node(name)
        self.image = None
        self.running = True
        self.fps = fps.FPS()
        signal.signal(signal.SIGINT, self.shutdown)
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
        self.mp_pose = mp.solutions.pose
        self.camera_type = os.environ.get('DEPTH_CAMERA_TYPE')
        rospy.Subscriber('/depth_cam/rgb/image_raw', Image, self.image_callback)  # 摄像头订阅
        self.run()

    def shutdown(self, signum, frame):
        self.running = False

    def image_callback(self, ros_image):
        self.image = np.ndarray(shape=(ros_image.height, ros_image.width, 3), dtype=np.uint8, buffer=ros_image.data) # 原始 RGB 画面
    
    def run(self):
        with self.mp_selfie_segmentation.SelfieSegmentation(model_selection=1) as selfie_segmentation:
            bg_image = None
            while self.running:
                if self.image is not None:
                    self.image.flags.writeable = False
                    image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                    results = selfie_segmentation.process(image)

                    image.flags.writeable = True
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    
                    condition = np.stack((results.segmentation_mask[:, :, 0],) * 3, axis=-1) > 0.1

                    if bg_image is None:
                        bg_image = np.zeros(image.shape, dtype=np.uint8)
                        bg_image[:] = BG_COLOR
                    output_image = np.where(condition, image, bg_image)
                    self.fps.update()
                    result_image = self.fps.show_fps(output_image)
                    # result_image = self.fps.show_fps(cv2.flip(image, 1))
                    result_image = cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR) if self.camera_type == 'usb_cam' else result_image
                    cv2.imshow('MediaPipe Pose', result_image)
                    key = cv2.waitKey(10)
                    if key != -1:
                        break
                else:
                    rospy.sleep(0.01)

if __name__ == '__main__':
    PoseNode('Pose')
