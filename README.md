# ROSOrin

English | [中文](https://github.com/Hiwonder/ROSOrin/blob/ROS1/README_cn.md)

<p align="center">
  <img src="./sources/images/rosorin.png" alt="ROSOrin Logo" width="600"/>
</p>

## Product Overview

ROSOrin is an advanced ROS-based robot development platform developed by Hiwonder, powered by NVIDIA Jetson Orin. It provides a comprehensive robotics development environment with ROS1 (Noetic) support, enabling advanced AI and robotics applications including SLAM, navigation, computer vision, and voice interaction.

ROSOrin is designed for robotics education, research, and development, offering a complete open-source software stack for learning and implementing state-of-the-art robotics algorithms.

## Official Resources

### Official Hiwonder
- **Official Website**: [https://www.hiwonder.com/](https://www.hiwonder.com/)
- **Technical Support**: support@hiwonder.com

## Key Features

### SLAM and Navigation
- **Gmapping** - Grid-based SLAM mapping
- **Cartographer** - Google Cartographer SLAM
- **AMCL Navigation** - Adaptive Monte Carlo Localization
- **Move Base** - Path planning and obstacle avoidance

### AI Vision
- **Object Detection** - Real-time object recognition
- **Color Tracking** - Color-based target tracking
- **Face Detection** - Face recognition capabilities
- **Gesture Recognition** - Hand gesture control

### Voice Interaction
- **Offline ASR** - iFlytek offline speech recognition
- **Voice Commands** - Voice-controlled robot operation
- **TTS** - Text-to-speech synthesis

### Multi-Robot Control
- **Multi-robot Coordination** - Coordinated multi-robot operation
- **Communication** - Inter-robot communication

## Hardware Configuration
- **Processor**: NVIDIA Jetson Orin
- **OS**: Ubuntu 20.04 + ROS1 Noetic
- **Sensors**: LiDAR, Camera, IMU
- **Communication**: WiFi, Ethernet

## Project Structure

```
ros1_src/
├── command/                 # Command scripts
└── src/
    ├── app/                 # Application packages
    ├── bringup/             # Launch configurations
    ├── calibration/         # Calibration tools
    ├── driver/              # Hardware drivers
    ├── navigation/          # Navigation stack
    ├── slam/                # SLAM packages
    └── xf_mic_asr_offline/  # Voice recognition
```

## Version Information
- **ROS Version**: ROS1 Noetic
- **Ubuntu Version**: 20.04 LTS

---

**Note**: This is the ROS1 branch. For ROS2 version, please switch to the ROS2 branch.
