# ROSOrin

[English](https://github.com/Hiwonder/ROSOrin/blob/ROS2/README.md) | 中文

<p align="center">
  <img src="./sources/images/rosorin.png" alt="ROSOrin Logo" width="600"/>
</p>

## 产品概述

ROSOrin 是由幻尔科技（Hiwonder）开发的基于 ROS 的高级机器人开发平台，搭载 NVIDIA Jetson Orin。它提供了完整的机器人开发环境，支持 ROS2（Humble），可实现 SLAM、导航、计算机视觉、语音交互和 AI 大模型集成等高级 AI 和机器人应用。

ROSOrin 专为机器人教育、研究和开发设计，提供完整的开源软件栈，用于学习和实现最先进的机器人算法。

## 官方资源

### 幻尔科技官方
- **官方网站**: [https://www.hiwonder.com/](https://www.hiwonder.com/)
- **技术支持**: support@hiwonder.com

## 主要功能

### SLAM 和导航
- **Cartographer** - Google Cartographer SLAM
- **SLAM Toolbox** - ROS2 SLAM 解决方案
- **Nav2** - ROS2 导航栈
- **路径规划** - 高级路径规划和避障

### AI 视觉
- **目标检测** - 实时目标识别
- **颜色跟踪** - 基于颜色的目标跟踪
- **人脸检测** - 人脸识别功能
- **手势识别** - 手势控制

### 语音交互
- **离线语音识别** - 讯飞离线语音识别
- **语音命令** - 语音控制机器人
- **语音合成** - 文字转语音

### AI 大模型
- **大语言模型集成** - 大语言模型支持
- **智能对话** - 自然语言交互
- **AI 助手** - 机器人 AI 助手功能

### 多机控制
- **多机协调** - 多机器人协同操作
- **通信** - 机器人间通信

## 硬件配置
- **处理器**: NVIDIA Jetson Orin
- **操作系统**: Ubuntu 22.04 + ROS2 Humble
- **传感器**: 激光雷达、摄像头、IMU
- **通信方式**: WiFi、以太网

## 项目结构

```
src_ros2/
├── command                  # 命令脚本
└── src/
    ├── app/                 # 应用程序包
    ├── bringup/             # 启动配置
    ├── calibration/         # 校准工具
    ├── driver/              # 硬件驱动
    ├── example/             # 示例代码
    ├── interfaces/          # ROS2 接口
    ├── large_models/        # AI 大模型集成
    ├── large_models_examples/ # 大模型示例
    ├── multi/               # 多机控制
    ├── navigation/          # 导航栈
    ├── peripherals/         # 外设驱动
    ├── simulations/         # Gazebo 仿真
    ├── slam/                # SLAM 包
    └── xf_mic_asr_offline/  # 语音识别
```

## 版本信息
- **ROS 版本**: ROS2 Humble
- **Ubuntu 版本**: 22.04 LTS

---

**注意**: 这是 ROS2 分支。如需 ROS1 版本，请切换到 ROS1 分支。
