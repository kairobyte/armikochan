# Armikochan V2 8-DOF Robotic Arm 🦾🐈‍⬛

![ROS2](https://img.shields.io/badge/ROS2-Jazzy-blue)
![License](https://img.shields.io/badge/License-Open%20Source%20(Coming%20Soon)-green)

This project is my 200+ day journey of building a high-precision, 8-degree-of-freedom robotic arm from scratch while surviving Electrical Engineering.

## 🚀 The Vision
Moving beyond simple 'open/close' mechanics, this project features a distributed PC-ESP32 architecture with integrated force-sensitivity. This allows the gripper to dynamically adjust its grasp pressure, ensuring safe and reliable handling of diverse payloads, from industrial parts to delicate items.
## 📂 Repository Contents

* **`/1. firmware`**: ESP32 code for low-latency motor driving and FSR sensor processing.
* **`/2. ros_ws`**: The heart of the robot. Contains the URDF, MoveIt2 configurations, and MoveIt Servo nodes for real-time control.
* **`/3. 3D Model`**: 3D models (STL/STEP) including my custom-designed planetary gear systems and the new "Control Module."
* **`/docs`**: Technical blogs and design notes on solving EMI issues and closed-loop calibration. (You won't see this directory yet. I'm still working on it.)

## 🛠️ Tech Stack
* **Software:** ROS2 Jazzy, MoveIt2, Solidworks.
* **Brain:** PC/Laptop ↔️ Raspberry Pi ↔️ ESP32.
* **Motors:** Nema 17 Stepper Motor.
* **Tactile:** Force-Sensitive Resistors (FSR) with silicone layer.

## 🚧 Current Status:
- [x] 8-DOF Mechanical Assembly
- [x] URDF & Rviz Integration
- [x] MoveIt Servo Real-time Control

## 🤝 Community & Support
I am a solo student developer balancing college, coding, and hardware. If you find this project helpful:
* **Follow the Journey:** [@kairobyte](https://instagram.com/kairobyte) on Instagram for weekly updates.
* **Visit the Site:** [kairobyte.com](https://kairobyte.com) for in-depth engineering blogs and the Open Source waitlist.

## 📥 Getting Started
```bash
# Clone the repository
git clone https://github.com/kairobyte/armikochan.git

# Navigate to the workspace
cd armikochan/2.\ ros_ws/

# Build the project
colcon build --symlink-install

# Source and Launch (Refer to /docs for specific launch files)
source install/setup.bash
