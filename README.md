# ROSOrin

English | [中文](https://github.com/Hiwonder/ROSOrin/blob/ROS2/README_cn.md)

<p align="center">
  <img src="./sources/images/rosorin.png" alt="ROSOrin Logo" width="600"/>
</p>

## The Open-Source Multimodal AI Robot on ROS2

This repository showcases a collection of demos, examples, and open-source modules for ROSOrin, a highly integrated ROS2 robot built for the next generation of embodied AI. Imagine a platform that brings together multimodal large models, real-time 3D vision, LiDAR navigation, and modular chassis design — all running on a Jetson-powered system. ROSOrin isn't just another robot kit; it's a playground for researchers, developers, and robotics enthusiasts who want to experiment with cutting-edge AI in the physical world.

<p align="center">
  <img src="./sources/images/rosorin1.png" alt="ROSOrin Autonomous Driving" width="400"/>
  <img src="./sources/images/rosorin2.png" alt="ROSOrin Navigation" width="400"/>
</p>

<p align="center">
  <img src="./sources/images/rosorin3.png" alt="ROSOrin AI Tracking" width="400"/>
  <img src="./sources/images/rosorin4.png" alt="ROSOrin SLAM" width="400"/>
</p>

## 🧠 What Makes This Robot Special

ROSOrin merges hardware versatility with advanced AI software in one cohesive platform. It comes equipped with LiDAR, a 3D depth camera, and a six-microphone array, enabling tasks like SLAM navigation, 3D object recognition, and voice interaction out of the box. Beyond traditional robotics, it integrates a openAI-based multimodal AI model for high-level task planning and environment understanding. Whether you're building an autonomous driving prototype, experimenting with YOLOv11 and MediaPipe for vision, or switching between Mecanum, Ackermann, and differential drive chassis — this robot is designed to adapt and grow with your projects.

## 🚀 Start Building With Full Open-Source Access

While this repository provides a glimpse into ROSOrin's capabilities, the complete source code, detailed tutorials, and AI project examples are available with the robot. If you're looking to dive deeper into ROS2 development, explore multimodal AI applications, or create a custom robot that can see, hear, and navigate intelligently, check out the official product page below to get started. Let's build the future of robotics, one commit at a time.



## Official Resources

### Official Hiwonder
- **Product Page**: [https://www.hiwonder.com/products/rosorin](https://www.hiwonder.com/products/rosorin)
- **Video**: [https://www.youtube.com/watch?v=b_mb6qqGgI4](https://www.youtube.com/watch?v=b_mb6qqGgI4)
- **Documentation**: [https://docs.hiwonder.com/projects/ROSOrin/en/jetson-orin-nano-version/](https://docs.hiwonder.com/projects/ROSOrin/en/jetson-orin-nano-version/)
- **Official Website**: [https://www.hiwonder.com/](https://www.hiwonder.com/)
- **Technical Support**: support@hiwonder.com

### YouTube Shorts
- **Tired of 1 robot 1 chassis?** 😴 Say Hi to ROSOrin! 🤖✨ [Watch](https://www.youtube.com/shorts/jrIz2km8RhI)
- **Lidar sees it all!** 🤖More Than Just Measure! 📡 [Watch](https://www.youtube.com/shorts/wyZXHAtLG7Q)
- **The Secret Sauce?** 👀 Large Vision Models! 🧠 [Watch](https://www.youtube.com/shorts/kxEU1YfewVM)
- **Guess what happens when you ✌️ at a robot?** [Watch](https://www.youtube.com/shorts/JHz-59gQs6s)

## Key Features

### SLAM and Navigation
- **Cartographer** - Google Cartographer SLAM
- **SLAM Toolbox** - ROS2 SLAM solution
- **Nav2** - ROS2 Navigation Stack
- **Path Planning** - Advanced path planning and obstacle avoidance

### AI Vision
- **Object Detection** - Real-time object recognition
- **Color Tracking** - Color-based target tracking
- **Face Detection** - Face recognition capabilities
- **Gesture Recognition** - Hand gesture control

### Voice Interaction
- **Offline ASR** - iFlytek offline speech recognition
- **Voice Commands** - Voice-controlled robot operation
- **TTS** - Text-to-speech synthesis

### AI Large Models
- **LLM Integration** - Large language model support
- **Intelligent Dialogue** - Natural language interaction
- **AI Assistant** - Robot AI assistant capabilities

### Multi-Robot Control
- **Multi-robot Coordination** - Coordinated multi-robot operation
- **Communication** - Inter-robot communication

## Hardware Configuration
- **Processor**: NVIDIA Jetson Orin
- **OS**: Ubuntu 22.04 + ROS2 Humble
- **Sensors**: LiDAR, Camera, IMU
- **Communication**: WiFi, Ethernet

## Project Structure

```
src_ros2/
├── command                  # Command scripts
└── src/
    ├── app/                 # Application packages
    ├── bringup/             # Launch configurations
    ├── calibration/         # Calibration tools
    ├── driver/              # Hardware drivers
    ├── example/             # Example code
    ├── interfaces/          # ROS2 interfaces
    ├── large_models/        # AI large model integration
    ├── large_models_examples/ # Large model examples
    ├── multi/               # Multi-robot control
    ├── navigation/          # Navigation stack
    ├── peripherals/         # Peripheral drivers
    ├── simulations/         # Gazebo simulation
    ├── slam/                # SLAM packages
    └── xf_mic_asr_offline/  # Voice recognition
```

## Version Information
- **ROS Version**: ROS2 Humble
- **Ubuntu Version**: 22.04 LTS

---

**Note**: This is the ROS2 branch. For ROS1 version, please switch to the ROS1 branch.
