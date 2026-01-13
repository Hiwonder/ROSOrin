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
        self.mp_objectron = mp.solutions.objectron
        self.mp_pose = mp.solutions.pose
        self.camera_type = os.environ.get('DEPTH_CAMERA_TYPE')
        rospy.Subscriber('/depth_cam/rgb/image_raw', Image, self.image_callback)  # 摄像头订阅
        self.run()

    def shutdown(self, signum, frame):
        self.running = False

    def image_callback(self, ros_image):
        self.image = np.ndarray(shape=(ros_image.height, ros_image.width, 3), dtype=np.uint8, buffer=ros_image.data) # 原始 RGB 画面
    
    def run(self):
        with self.mp_objectron.Objectron(static_image_mode=False,
                                max_num_objects=1,
                                min_detection_confidence=0.4,
                                min_tracking_confidence=0.5,
                                model_name='Cup') as objectron:
            while self.running:
                if self.image is not None:
                    self.image.flags.writeable = False
                    image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                    results = objectron.process(image)

                    image.flags.writeable = True
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    
                    if results.detected_objects:
                        for detected_object in results.detected_objects:
                            self.mp_drawing.draw_landmarks(
                            image, detected_object.landmarks_2d, self.mp_objectron.BOX_CONNECTIONS)
                            self.mp_drawing.draw_axis(image, detected_object.rotation,
                                                detected_object.translation)
                    self.fps.update()
                    result_image = self.fps.show_fps(image)
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
