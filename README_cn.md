# ROSOrin

[English](https://github.com/Hiwonder/ROSOrin/blob/ROS1/README.md) | 中文

<p align="center">
  <img src="./sources/images/rosorin.png" alt="ROSOrin Logo" width="600"/>
</p>

## 基于ROS1的开源多模态AI机器人

本仓库展示了ROSOrin的演示、示例和开源模块集合。ROSOrin是一款高度集成的ROS1机器人，专为下一代具身AI而打造。它将多模态大模型、实时3D视觉、激光雷达导航和模块化底盘设计融为一体，全部运行在Jetson驱动的系统上。ROSOrin不仅仅是一个机器人套件，更是研究人员、开发者和机器人爱好者探索前沿AI的实验平台。

## 官方资源

### 幻尔科技官方
- **产品页面**: [https://www.hiwonder.com/products/rosorin](https://www.hiwonder.com/products/rosorin)
- **视频**: [https://www.youtube.com/watch?v=b_mb6qqGgI4](https://www.youtube.com/watch?v=b_mb6qqGgI4)
- **教程文档**: [https://docs.hiwonder.com/projects/ROSOrin/en/jetson-orin-nano-version/](https://docs.hiwonder.com/projects/ROSOrin/en/jetson-orin-nano-version/)
- **官方网站**: [https://www.hiwonder.com/](https://www.hiwonder.com/)
- **技术支持**: support@hiwonder.com

## 主要功能

### SLAM 和导航

<p align="center">
  <img src="./sources/images/rosorin2.png" alt="ROSOrin导航" width="600"/>
  <img src="./sources/images/rosorin4.png" alt="ROSOrin SLAM" width="600"/>
</p>

- **Gmapping** - 基于栅格的 SLAM 建图
- **Cartographer** - Google Cartographer SLAM
- **AMCL 导航** - 自适应蒙特卡洛定位
- **Move Base** - 路径规划和避障

### AI 视觉

<p align="center">
  <img src="./sources/images/rosorin3.png" alt="ROSOrin AI视觉" width="600"/>
</p>

- **目标检测** - 实时目标识别
- **颜色跟踪** - 基于颜色的目标跟踪
- **人脸检测** - 人脸识别功能
- **手势识别** - 手势控制

### 语音交互
- **离线语音识别** - 讯飞离线语音识别
- **语音命令** - 语音控制机器人
- **语音合成** - 文字转语音

### 多机控制
- **多机协调** - 多机器人协同操作
- **通信** - 机器人间通信

## 硬件配置
- **处理器**: NVIDIA Jetson Orin
- **操作系统**: Ubuntu 20.04 + ROS1 Noetic
- **传感器**: 激光雷达、摄像头、IMU
- **通信方式**: WiFi、以太网

## 版本信息
- **ROS 版本**: ROS1 Noetic
- **Ubuntu 版本**: 20.04 LTS

---

**注意**: 这是 ROS1 分支。如需 ROS2 版本，请切换到 ROS2 分支。
