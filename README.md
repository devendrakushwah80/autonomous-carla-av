# 🚗 Autonomous Driving System in CARLA

A hybrid autonomous driving system built using the CARLA simulator that integrates rule-based navigation and deep learning perception.

The system demonstrates real-time autonomous driving with object detection, traffic awareness, and 3D environment understanding.

---

## 🎥 Demo

(Add demo GIF or video here)

---

## 🧠 System Architecture

Simulation → Sensors → Perception → Planning → Control → Visualization

```
CARLA Simulator
↓
RGB + Semantic Cameras
↓
Perception
├ YOLOv8 Object Detection
├ Semantic Road Segmentation
└ 3D Bounding Box Projection
↓
BehaviorAgent Navigation
↓
Vehicle Control
↓
Visualization Dashboard
```

---

## 🚀 Features

- Autonomous driving using **CARLA BehaviorAgent**
- **YOLOv8 object detection**
- **Semantic road segmentation overlay**
- **3D projected vehicle bounding boxes**
- **Traffic light awareness**
- **Real-time performance monitoring**
- CPU / GPU usage tracking
- FPS monitoring

---

## 🛠 Technologies Used

| Component | Technology |
|--------|-------------|
| Simulator | CARLA |
| Language | Python |
| Object Detection | YOLOv8 |
| Visualization | OpenCV |
| Deep Learning | PyTorch |
| Monitoring | psutil / GPUtil |

---

## 📂 Project Structure

```
autonomous-carla-av/
│
├── app/
│ └── main.py
│
├── core/
│ ├── simulation/
│ │ ├── simulator.py
│ │ ├── vehicle_manager.py
│ │ └── sensors.py
│ │
│ ├── control/
│ │ └── pid_controller.py
│
├── configs/
│ └── config.py
```

---

## ⚙️ Installation

### 1️⃣ Clone repo

```
git clone https://github.com/YOUR_USERNAME/autonomous-carla-av.git
cd autonomous-carla-av
```

### 2️⃣ Install dependencies

```
pip install -r requirements.txt
```

### 3️⃣ Run CARLA Simulator

Start CARLA server.

### 4️⃣ Run project

```
python -m app.main
```

---

## 🎯 Results

- Stable autonomous driving
- Real-time object detection
- Traffic light compliance
- Smooth navigation in urban environment

---

## 🔮 Future Improvements

- LiDAR integration
- Sensor fusion
- Reinforcement learning control
- Trajectory planning
- Real-world deployment research

---

## 👨‍💻 Author

Devendra Kushwah

Machine Learning & Autonomous Systems Enthusiast