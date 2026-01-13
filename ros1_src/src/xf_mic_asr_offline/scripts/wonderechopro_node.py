#!/usr/bin/env python3
# coding=utf-8

import os
import time
import rospy
import signal
import serial
import binascii
from std_srvs.srv import Trigger
from std_msgs.msg import String, Bool


zh_cmd = ['拔个萝卜',
          '拿给我',
          '开启颜色识别',
          '关闭颜色识别',
          '开启颜色分拣',
          '关闭颜色分拣',
          '追踪红色',
          '追踪绿色',
          '追踪蓝色',
          '停止追踪',
          '夹取红色',
          '夹取绿色',
          '夹取蓝色',
          '夹取球体',
          '夹取圆柱体',
          '夹取立方体',
          '关闭夹取',
          '开启垃圾分类',
          '关闭垃圾分类',
          '前进',
          '后退',
          '左转',
          '右转',
          '停下',
          '漂移',
          '过来',
          '去A点',
          '去B点',
          '去C点',
          '回原点',
          '导航搬运']


en_cmd = ['pick a carrot',
          'pass me please',
          'start color recognition',
          'stop color recognition',
          'start color sorting',
          'stop color sorting',
          'track red object',
          'track green object',
          'track blue object',
          'stop tracking',
          'gripping red',
          'gripping green',
          'gripping blue',
          'gripping the sphere',
          'gripping the cylinder',
          'gripping the cuboid',
          'stop gripping',
          'sort waste',
          'stop sort waste',
          'go forward',
          'go backward',
          'turn left',
          'turn right',
          'stop',
          'drift',
          'come here',
          'go to A point',
          'go to B point',
          'go to C point',
          'go back to the start',
          'navigate and transport']


class ASRNode:
    def __init__(self, name):
        rospy.init_node(name)
        self.wake_up = False
        self.wake_up_agreement = 'aa550300fb'
        self.sleep_agreement = 'aa550200fb'
        self.language = os.environ['ASR_LANGUAGE']

        if self.language == 'Chinese':
            self.receiving_agreement = {
                'aa550300fb': '唤醒成功(wake-up-success)',
                'aa550200fb': '休眠(Sleep)'
            }
            start = 0
            frame = "aa550001fb"
            for i in zh_cmd:
                start += 1
                frame = frame[:6] + str(format(start, '02x')) + frame[8:]
                self.receiving_agreement[frame] = i

        elif self.language == 'English':
            self.receiving_agreement = {
                'aa550300fb': '唤醒成功(wake-up-success)',
                'aa550200fb': '休眠(Sleep)'
            }
            start = 0
            frame = "aa550001fb"
            for i in en_cmd:
                start += 1
                frame = frame[:6] + str(format(start, '02x')) + frame[8:]
                self.receiving_agreement[frame] = i
        else:
            rospy.logerr("ASR_LANGUAGE environment variable not set or invalid. Please set to 'Chinese' or 'English'.")
            return

        self.control = rospy.Publisher('~voice_words', String, queue_size=1)

        self.ser = serial.Serial('/dev/ring_mic', 115200, timeout=1)

        print('\033[1;32mstart\033[0m')

        self.last_recognition_time = time.time()
        self.main()

    def main(self):
        while not rospy.is_shutdown():
            if self.ser.in_waiting > 0:
                data = self.ser.read(self.ser.in_waiting)  # 读取所有缓冲区中的数据
                hex_data = binascii.hexlify(data).decode('utf-8')

                if not self.wake_up and hex_data == self.wake_up_agreement:
                    ward = self.receiving_agreement[hex_data]
                    print('\033[1;32m%s\033[0m' % ward)
                    self.wake_up = True
                    self.last_recognition_time = time.time()  # 唤醒成功后重置计时器
                    count_msg = String()
                    count_msg.data = ward
                    self.control.publish(count_msg)

                elif self.wake_up:
                    if hex_data == self.sleep_agreement:
                        ward = self.receiving_agreement[hex_data]
                        print('\033[1;32m%s\033[0m' % ward)
                        self.wake_up = False # 退出唤醒状态
                        count_msg = String()
                        count_msg.data = ward
                        self.control.publish(count_msg)
                    elif hex_data in self.receiving_agreement:
                        ward = self.receiving_agreement[hex_data]
                        print('\033[1;32m%s\033[0m' % ward)
                        self.wake_up = False  # 识别完关键词后，重置唤醒标志
                        self.last_recognition_time = time.time()  # 识别到词语时重置计时器
                        count_msg = String()
                        count_msg.data = ward
                        self.control.publish(count_msg)

            if self.wake_up and (time.time() - self.last_recognition_time > 5):
                self.last_recognition_time = time.time()  # 重置计时器，避免重复输出


if __name__ == "__main__":
    try:
        ASRNode('asr_node')
    except rospy.ROSInterruptException:
        pass