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

class FaceMeshNode:
    def __init__(self, name):
        rospy.init_node(name)
        self.image = None
        self.running = True
        self.fps = fps.FPS()
        signal.signal(signal.SIGINT, self.shutdown)
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_face_mesh = mp.solutions.face_mesh
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
        self.camera_type = os.environ.get('DEPTH_CAMERA_TYPE')
        rospy.Subscriber('/depth_cam/rgb/image_raw', Image, self.image_callback)  # 摄像头订阅
        self.run()

    def shutdown(self, signum, frame):
        self.running = False

    def image_callback(self, ros_image):
        self.image = np.ndarray(shape=(ros_image.height, ros_image.width, 3), dtype=np.uint8, buffer=ros_image.data) # 原始 RGB 画面
    
    def run(self):
        with self.mp_face_mesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
            while self.running:
                if self.image is not None:
                    self.image.flags.writeable = False
                    image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                    results = face_mesh.process(image)
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    image.flags.writeable = True
                    if results.multi_face_landmarks:
                      for face_landmarks in results.multi_face_landmarks:
                         self.mp_drawing.draw_landmarks(
                            image=image,
                            landmark_list=face_landmarks,
                            landmark_drawing_spec=self.drawing_spec)
                    self.fps.update()
                    result_image = self.fps.show_fps(cv2.flip(image, 1))
                    result_image = cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR) if self.camera_type == 'usb_cam' else result_image
                    cv2.imshow('MediaPipe Face Mesh', result_image)
                    key = cv2.waitKey(10)
                    if key != -1:
                        break
                else:
                    rospy.sleep(0.01)

if __name__ == '__main__':
    FaceMeshNode('FaceMesh')
