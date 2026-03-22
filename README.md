# 🚗 Autonomous Driving System using CARLA & YOLOv8

A hybrid autonomous driving system built using the **CARLA Simulator** that integrates **rule-based navigation** with **deep learning perception**.

The system demonstrates **real-time autonomous driving**, **object detection**, **traffic awareness**, and **3D environment understanding** in a simulated urban environment.

---

# 📌 Project Overview

Autonomous vehicles must understand their environment, plan routes, and control the vehicle safely.

This project simulates a **mini autonomous driving stack** consisting of:

* Environment simulation
* Sensor data acquisition
* Deep learning perception
* Navigation planning
* Vehicle control
* Visualization dashboard

All components run in real time inside the **CARLA autonomous driving simulator**.

---

# 🎥 Demo Video

[Watch here.](https://www.linkedin.com/posts/devendrakushwah80_autonomousdriving-artificialintelligence-ugcPost-7441144910948433920-5wLo?utm_source=social_share_send&utm_medium=member_desktop_web&rcm=ACoAAFKb1C0BG6XD6smJ84paZW2MeGcSug6XIvA)

Example:

```
demo/demo.gif
```

Recommended screenshots:

* Front camera view
* YOLO object detection
* Eagle-eye top view
* 3D bounding boxes

---

# 🧠 System Architecture

The system follows a simplified autonomous driving pipeline:

```
CARLA Simulator
        ↓
RGB + Semantic Cameras
        ↓
Perception Module
   ├ YOLOv8 Object Detection
   ├ Semantic Road Segmentation
   └ 3D Bounding Box Projection
        ↓
Navigation (BehaviorAgent)
        ↓
Vehicle Control
        ↓
Visualization Dashboard
```

This architecture mimics the structure used in **real autonomous vehicle systems**.

---

# 🚀 Key Features

### 🚗 Autonomous Navigation

Uses CARLA's **BehaviorAgent** for rule-based navigation and path planning.

### 👁️ Real-time Object Detection

Detects surrounding vehicles using **YOLOv8 deep learning model**.

### 🛣 Semantic Road Segmentation

Semantic camera identifies road surfaces to understand the environment.

### 📦 3D Bounding Box Projection

Projects CARLA vehicle bounding boxes onto the camera image for spatial visualization.

### 🚦 Traffic Light Awareness

Vehicle reads the traffic light state from the simulator.

### ⚠️ Collision Warning System

Warns when vehicles are too close and applies emergency braking.

### 🖥 Visualization Dashboard

Displays real-time system data including:

* Speed
* FPS
* CPU usage
* GPU usage
* Traffic light state
* Collision warnings

### 🦅 Eagle-Eye Monitoring View

Top-down camera provides a bird-eye view of the simulation.

---

# 🛠 Technologies Used

| Component              | Technology      |
| ---------------------- | --------------- |
| Simulator              | CARLA           |
| Programming Language   | Python          |
| Deep Learning          | PyTorch         |
| Object Detection       | YOLOv8          |
| Computer Vision        | OpenCV          |
| Performance Monitoring | psutil / GPUtil |

---

# 📂 Project Structure

```
autonomous-carla-av/
│
├── app/
│   └── main.py
│
├── core/
│   ├── simulation/
│   │   ├── simulator.py
│   │   ├── vehicle_manager.py
│   │   └── sensors.py
│   │
│   ├── control/
│   │   └── pid_controller.py
│
├── configs/
│   └── config.py
│
└── README.md
```

---

# ⚙️ Installation

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/devendrakushwah80/autonomous-carla-av.git
cd autonomous-carla-av
```

---

## 2️⃣ Install Dependencies

Create virtual environment (recommended):

```bash
python -m venv venv
venv\Scripts\activate
```

Install packages:

```bash
pip install -r requirements.txt
```

---

## 3️⃣ Run CARLA Simulator

Download CARLA:

https://carla.org/

Run the simulator:

```
CarlaUE4.exe
```

---

## 4️⃣ Run the Autonomous System

```bash
python -m app.main
```

---

# 📊 System Outputs

The system provides the following outputs:

### Front Camera View

Displays:

* object detection
* semantic overlay
* 3D vehicle boxes

### Eagle-Eye View

Top-down monitoring of the simulation.

### Performance Dashboard

Displays:

* Speed
* FPS
* CPU usage
* GPU usage
* Traffic light state
* Collision warnings

---

# 🎯 Results

The system successfully demonstrates:

* Autonomous navigation in CARLA
* Real-time deep learning perception
* Collision warning system
* Traffic light awareness
* Smooth vehicle navigation

---

# 🔮 Future Improvements

Possible future enhancements include:

* LiDAR sensor integration
* Multi-sensor fusion
* Lane detection algorithms
* Reinforcement learning based control
* Pedestrian avoidance system
* Autonomous overtaking
* Real-world autonomous vehicle research

---

# 👨‍💻 Author

**Devendra Kushwah**

Machine Learning & Autonomous Systems Enthusiast

---
🍴 Fork the project
🤝 Contribute improvements
