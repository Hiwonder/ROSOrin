# ROSOrin

English | [中文](https://github.com/Hiwonder/ROSOrin/blob/ROS2/README_cn.md)

<p align="center">
  <img src="./sources/images/rosorin.png" alt="ROSOrin Logo" width="600"/>
</p>

## Product Overview

ROSOrin is an advanced ROS-based robot development platform developed by Hiwonder, powered by NVIDIA Jetson Orin. It provides a comprehensive robotics development environment with ROS2 (Humble) support, enabling advanced AI and robotics applications including SLAM, navigation, computer vision, voice interaction, and AI large model integration.

ROSOrin is designed for robotics education, research, and development, offering a complete open-source software stack for learning and implementing state-of-the-art robotics algorithms.

## Official Resources

### Official Hiwonder
- **Official Website**: [https://www.hiwonder.com/](https://www.hiwonder.com/)
- **Technical Support**: support@hiwonder.com

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
