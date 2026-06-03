# ARMIKOCHAN V2: 8 AXIS ROBOTIC ARM

![ROS2](https://img.shields.io/badge/ROS2-Jazzy-blue)
![License](https://img.shields.io/badge/License-Open%20Source%20-green)

This project is my 200+ day journey of building a high-precision, 8-degree-of-freedom robotic arm from scratch.

## The Vision

Most robotic arms out there are 6DOF at best, and they easily cost upwards of $5000. For a student or a smaller college, that's just not realistic. The ones that do offer more capability are either proprietary, locked behind expensive licenses, or simply too complex to learn from. There's a huge gap between what's available and what's actually accessible, and that gap is what this project is trying to fill.

<img src="5. readme_assets/3d-model.png" alt="3d-model" height="300"> <img src="5. readme_assets/robot-pic-2.jpg" alt="robot image" height="300">

## Repository Contents

- **`/1. firmware`**: ESP32 code for low-latency motor driving and FSR sensor processing.
- **`/2. ros_ws`**: The heart of the robot. Contains the URDF, MoveIt2 configurations, and MoveIt Servo nodes for real-time control.
- **`/3. 3D Model`**: 3D models (STL/SLDPRT) including my custom-designed planetary gear systems.
- **`/4. docs`**: Technical blogs and design notes.
- **`/5. readme_assets`**: Contains images for README.md file

## Tech Stack

- **Software:** Ubuntu 24.04, ROS2 Jazzy, MoveIt2, Solidworks, OpenCV
- **Brain:** PC/Laptop <-> Raspberry Pi <-> ESP32.
- **Actuators:** Nema 17 Stepper Motor, with custom designed planetary gear set.
- **Feedback:** Force-Sensitive Resistors (FSR) with silicone layer for gripper feedback and AS5600 magnetic encoder for joint angle feedback.

## Block Diagram
<img src="5. readme_assets/block-diagram.png" alt="block diagram">

## Community & Support

I am a solo student developer balancing college, coding, and hardware. If you find this project helpful:

- **Follow the Journey:** [@kairobyte](https://instagram.com/kairobyte) on Instagram.
- **Visit the Site:** [kairobyte.com](https://kairobyte.com) for in-depth engineering blogs.

## Getting Started

```bash
# Clone the repository
git clone https://github.com/kairobyte/armikochan.git

# Navigate to the workspace
cd armikochan/2.\ ros_ws/

# Build the project
colcon build --symlink-install

# Source and Launch (Refer to /docs for specific launch files)
source install/setup.bash
```

## Next Steps:

- The shoulder joint could be made bidirectional, which would help reduce the sag a lot.
- Using slip rings instead of passing the wires through the cavity inside the actuators would significantly increase the workspace of the arm.

Lastly, I'll be the first to admit, building something like this alone is difficult. And when you're doing it all by yourself, your perspective is limited. So not everything is done the most efficient way, and there's honestly a lot of room for improvement.
