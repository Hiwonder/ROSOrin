# ROSOrin

English | [中文](https://github.com/Hiwonder/ROSOrin/blob/ROS1/README_cn.md)

<p align="center">
  <img src="./sources/images/rosorin.png" alt="ROSOrin Logo" width="600"/>
</p>

## The Open-Source Multimodal AI Robot on ROS1

This repository showcases a collection of demos, examples, and open-source modules for ROSOrin, a highly integrated ROS1 robot built for the next generation of embodied AI. Imagine a platform that brings together multimodal large models, real-time 3D vision, LiDAR navigation, and modular chassis design — all running on a Jetson-powered system. ROSOrin isn't just another robot kit; it's a playground for researchers, developers, and robotics enthusiasts who want to experiment with cutting-edge AI in the physical world.

## Official Resources

### Official Hiwonder
- **Product Page**: [https://www.hiwonder.com/products/rosorin](https://www.hiwonder.com/products/rosorin)
- **Video**: [https://www.youtube.com/watch?v=b_mb6qqGgI4](https://www.youtube.com/watch?v=b_mb6qqGgI4)
- **Documentation**: [https://docs.hiwonder.com/projects/ROSOrin/en/jetson-orin-nano-version/](https://docs.hiwonder.com/projects/ROSOrin/en/jetson-orin-nano-version/)
- **Official Website**: [https://www.hiwonder.com/](https://www.hiwonder.com/)
- **Technical Support**: support@hiwonder.com

## Key Features

### SLAM and Navigation

<p align="center">
  <img src="./sources/images/rosorin2.png" alt="ROSOrin Navigation" width="400"/>
  <img src="./sources/images/rosorin4.png" alt="ROSOrin SLAM" width="400"/>
</p>

- **Gmapping** - Grid-based SLAM mapping
- **Cartographer** - Google Cartographer SLAM
- **AMCL Navigation** - Adaptive Monte Carlo Localization
- **Move Base** - Path planning and obstacle avoidance

### AI Vision

<p align="center">
  <img src="./sources/images/rosorin3.png" alt="ROSOrin AI Vision" width="400"/>
</p>

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
