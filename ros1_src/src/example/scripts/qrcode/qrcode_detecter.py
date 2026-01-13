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

MODEL_PATH = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'opencv_3rdparty')
model1 = os.path.join(MODEL_PATH, 'detect.prototxt')
model2 = os.path.join(MODEL_PATH, 'detect.caffemodel')
model3 = os.path.join(MODEL_PATH, 'sr.prototxt')
model4 = os.path.join(MODEL_PATH, 'sr.caffemodel')

detect_obj = cv2.wechat_qrcode_WeChatQRCode(model1, model2, model3, model4)

class QRcodeDetect():
    def __init__(self, name):
        rospy.init_node(name)
        self.image = None
        self.running = True
        self.fps = fps.FPS()
        signal.signal(signal.SIGINT, self.shutdown)
        self.camera_type = os.environ.get('DEPTH_CAMERA_TYPE')
        rospy.Subscriber('/depth_cam/rgb/image_raw', Image, self.image_callback)  # 摄像头订阅
        self.run()

    def shutdown(self, signum, frame):
        self.running = False

    def image_callback(self, ros_image):
        self.image = np.ndarray(shape=(ros_image.height, ros_image.width, 3), dtype=np.uint8, buffer=ros_image.data) # 原始 RGB 画面

    def run(self):
        while self.running:
            if self.image is not None:
                res, points = detect_obj.detectAndDecode(self.image)
                if res != ():
                    print('result:', res)
                for pos in points:
                    color = (0, 0, 255)
                    thick = 3
                    for p in [(0, 1), (1, 2), (2, 3), (3, 0)]:
                        start = int(pos[p[0]][0]), int(pos[p[0]][1])
                        end = int(pos[p[1]][0]), int(pos[p[1]][1])
                        cv2.line(self.image, start, end, color, thick)
                self.fps.update()
                result_image = self.fps.show_fps(self.image)
                result_image = cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR) if self.camera_type == 'usb_cam' else result_image
                cv2.imshow('qrcode_detect', result_image)
                key = cv2.waitKey(1)
                if key != -1: 
                    break
            else:
                rospy.sleep(0.01)

if __name__ == '__main__':
    QRcodeDetect('qrcode_detect')
