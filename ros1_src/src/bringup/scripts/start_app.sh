#!/bin/zsh

source /home/hiwonder/.zshrc
# 启动深度摄像头
echo "Starting depth camera..."
roslaunch peripherals depth_cam.launch depth_camera_name:="depth_cam" image_topic:="image_raw" &

# 等待摄像头启动完成
echo "Waiting for depth camera to initialize..."
sleep 10  # 延时10秒，可根据实际情况调整

# 启动底盘驱动
echo "Starting chassis driver..."
roslaunch controller controller.launch &

# 短暂延时确保底盘驱动启动
sleep 3

# 根据深度摄像头类型启动web视频服务器
if [ -n "$DEPTH_CAMERA_TYPE" ]; then
    echo "Starting web video server..."
    rosrun web_video_server web_video_server &
    sleep 2
fi

# 启动app通信
echo "Starting ROSBridge..."
roslaunch bringup rosbridge.launch &

sleep 2

# 启动app功能
echo "Starting app functions..."
roslaunch app start_app.launch &

sleep 2

# 启动手柄控制
echo "Starting joystick control..."
roslaunch peripherals joystick_control.launch &

sleep 2

# 启动开机自检
echo "Starting startup check..."
rosrun bringup startup_check.py &

echo "All components started!"

# 等待所有后台进程
wait
