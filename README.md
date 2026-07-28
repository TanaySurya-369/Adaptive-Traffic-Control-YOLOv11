<div align="center">

# 🚦 TrafficPilot AI

### Autonomous Traffic Management Agent using YOLOv11

> **AI-powered intelligent traffic signal optimization using Computer Vision, YOLOv11, and autonomous decision-making for smarter cities.**

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/Python-3.10+-orange.svg" alt="Python">
  <img src="https://img.shields.io/badge/Build-Passing-brightgreen.svg" alt="Build">
  <img src="https://img.shields.io/badge/YOLO-YOLOv11-red.svg" alt="YOLOv11">
  <img src="https://img.shields.io/github/repo-size/TanaySurya-369/Adaptive-Traffic-Control-YOLOv11" alt="Repository Size">
  <img src="https://img.shields.io/github/stars/TanaySurya-369/Adaptive-Traffic-Control-YOLOv11?style=social" alt="GitHub Stars">
</p>

**🚦 Intelligent • 🤖 Autonomous • ⚡ Real-Time • 🌍 Smart City Ready**

</div>

---

# 🌟 Overview

TrafficPilot AI is an **AI-powered Autonomous Traffic Management Agent** designed to improve urban traffic efficiency using **Computer Vision** and **Deep Learning**.

The system continuously monitors CCTV traffic feeds, detects vehicles using **YOLOv11**, estimates lane-wise traffic density, and autonomously adjusts traffic signal timings to improve traffic flow.

Unlike conventional fixed-time traffic lights, TrafficPilot AI dynamically responds to changing traffic conditions, enabling more efficient and intelligent traffic management while utilizing existing CCTV infrastructure.

---

# 🚀 Key Highlights

- 🤖 Autonomous AI Agent for intelligent traffic control
- 🚗 Real-time vehicle detection using YOLOv11
- 🚦 Dynamic traffic signal optimization
- 📊 Lane-wise congestion estimation
- 🎮 Interactive traffic simulation using Pygame
- 📹 Vision-based traffic monitoring
- ⚡ Utilizes existing CCTV infrastructure
- 🌍 Designed for Smart City applications
- 🧠 AI-driven decision engine
- 📈 Improved traffic efficiency through adaptive signal timing

---

# 📖 Table of Contents

- [Overview](#-overview)
- [Key Highlights](#-key-highlights)
- [Demo](#-demo)
- [Features](#-features)
- [Motivation](#-motivation)
- [Why TrafficPilot AI?](#-why-trafficpilot-ai)
- [Technology Stack](#-technology-stack)
- [System Architecture](#-system-architecture)
- [AI Agent Workflow](#-ai-agent-workflow)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Dataset & Model Weights](#-dataset--model-weights)
- [Results](#-results)
- [Screenshots](#-screenshots)
- [Future Roadmap](#-future-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Authors](#-authors)
- [Citation](#-citation)
- [Support](#-support)
- [Acknowledgements](#-acknowledgements)

---

# 🎬 Demo

TrafficPilot AI continuously monitors traffic through CCTV footage, detects vehicles using **YOLOv11**, estimates lane-wise congestion, and dynamically optimizes traffic signal timings using an autonomous decision engine.

### Simulation Preview

![Traffic Simulation](images/mod_int.png)

> 💡 **Tip:** Replace this image with a short demo GIF (`README_ASSETS/demo.gif`) to make the repository more engaging.

---

# ✨ Features

- 🚗 Real-time vehicle detection using YOLOv11
- 🚦 Adaptive traffic signal optimization
- 📹 Computer Vision-based traffic monitoring
- 📊 Lane-wise vehicle density estimation
- 🧠 Intelligent AI decision engine
- 🎮 Interactive traffic simulation
- ⚡ Low-cost deployment using existing CCTV cameras
- 🌍 Smart City compatible architecture
- 🔄 Continuous traffic monitoring
- 📈 Improved traffic flow through adaptive signal timing

---

# 🎯 Motivation

Traditional traffic lights operate using fixed signal timings regardless of the actual traffic conditions.

TrafficPilot AI addresses this limitation by continuously observing traffic conditions through computer vision and dynamically allocating signal timings based on real-time congestion.

This intelligent approach aims to improve traffic flow, reduce unnecessary waiting time, minimize fuel wastage, and support future smart city initiatives.

---

# 💡 Why TrafficPilot AI?

TrafficPilot AI is designed to make traffic management more intelligent without requiring expensive roadside sensors or additional hardware.

The system leverages existing CCTV infrastructure together with Artificial Intelligence to provide:

- 🚦 Adaptive signal control
- 🚗 Better traffic throughput
- ⏱ Reduced vehicle waiting time
- ⛽ Lower idle time
- 🌱 Environment-friendly traffic optimization
- 🌍 Scalable Smart City deployment

---

# 🛠️ Technology Stack

| Category | Technology |
|-----------|------------|
| Programming Language | Python |
| Computer Vision | OpenCV |
| AI Model | YOLOv11 |
| Deep Learning | PyTorch |
| Simulation | Pygame |
| Numerical Computing | NumPy |
| Version Control | Git & GitHub |

---

# 🏗️ System Architecture

TrafficPilot AI consists of four primary components working together to optimize urban traffic flow.

### Architecture Overview

- 📹 Traffic Monitoring
- 🚗 Vehicle Detection
- 🧠 AI Decision Engine
- 🚦 Adaptive Signal Optimization

```text
Camera
   │
   ▼
YOLOv11 Vehicle Detection
   │
   ▼
Lane-wise Traffic Density Estimation
   │
   ▼
AI Decision Engine
   │
   ▼
Adaptive Signal Timing
   │
   ▼
Traffic Simulation
```

> 📌 If available, you can also include an architecture image below.

```md
![System Architecture](docs/architecture.png)
```

---

# 🧠 AI Agent Workflow

```text
Live CCTV Feed
        │
        ▼
Vehicle Detection using YOLOv11
        │
        ▼
Lane-wise Density Analysis
        │
        ▼
Traffic Condition Assessment
        │
        ▼
AI Decision Engine
        │
        ▼
Adaptive Signal Timing
        │
        ▼
Traffic Simulation
        │
        ▼
Continuous Real-Time Optimization
```

---

# 📂 Project Structure

```text
Adaptive-Traffic-Control-YOLOv11/
│
├── .github/
│   └── workflows/
├── README_ASSETS/
├── docs/
├── examples/
├── scripts/
├── images/
├── sample_videos/
├── papers/
├── BADGES/
├── Merges.py
├── run.py
├── requirements.txt
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
└── NOTES_FOR_REVIEWERS.md
```

---

# ⚙️ Installation

### Prerequisites

Before running the project, ensure the following software is installed:

- Python 3.10 or later
- Git
- OpenCV dependencies
- PyTorch
- Pygame

Clone the repository:

```bash
git clone https://github.com/TanaySurya-369/Adaptive-Traffic-Control-YOLOv11.git

cd Adaptive-Traffic-Control-YOLOv11
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

**Windows**

```powershell
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Verify installation:

```bash
python --version
pip list
```

---

# 🚀 Quick Start

Download the official **YOLOv11** model weights from the Ultralytics repository.

Create a models directory if it doesn't already exist.

```text
models/
└── yolo11x.pt
```

Run traffic detection:

```bash
python Merges.py --input sample_videos/simulated_file_1.mp4 --mode detect
```

Run the traffic simulation:

```bash
python Merges.py --mode simulate
```

---

# 💻 Usage

### Vehicle Detection

```bash
python run.py \
--mode detect \
--input sample_videos/simulated_file_1.mp4 \
--weights models/yolo11x.pt
```

### Traffic Simulation

```bash
python run.py --mode simulate
```

### Example Workflow

1. Load CCTV footage.
2. Detect vehicles using YOLOv11.
3. Estimate lane-wise traffic density.
4. Calculate congestion level.
5. Optimize traffic signal timings.
6. Visualize traffic flow using the simulation.

---

# 📦 Dataset & Model Weights

This repository **does not include trained model weights** because of their large file size.

Download the official YOLOv11 weights and save them as:

```text
models/yolo11x.pt
```

> **Note:** Please do not commit or upload model weights to this repository.

---

# 📊 Results

TrafficPilot AI demonstrates the following capabilities during simulation:

- 🚦 Adaptive traffic signal allocation
- 🚗 Improved traffic throughput
- 📉 Reduced vehicle waiting time
- ⛽ Lower idle time and fuel consumption
- 🌱 Potential reduction in carbon emissions
- 🤖 Autonomous AI-based signal optimization

### Expected Benefits

| Metric | Improvement |
|---------|-------------|
| Traffic Flow | Improved |
| Vehicle Waiting Time | Reduced |
| Signal Efficiency | Increased |
| Fuel Consumption | Reduced |
| Smart City Readiness | Enhanced |

> **Note:** Results are based on the simulated environment used in this project. Actual performance may vary depending on traffic conditions, camera placement, hardware, and deployment configuration.

---

# 🔍 Implementation Pipeline

```text
Input CCTV Feed
        │
        ▼
Video Processing
        │
        ▼
YOLOv11 Object Detection
        │
        ▼
Vehicle Counting
        │
        ▼
Traffic Density Analysis
        │
        ▼
AI Decision Engine
        │
        ▼
Signal Timing Optimization
        │
        ▼
Traffic Simulation
```

---

# 🧪 Testing

The project has been tested with:

- Simulated traffic videos
- Multiple vehicle densities
- Four-way traffic intersection
- Real-time object detection
- Adaptive traffic signal allocation

The modular design also allows future integration with live CCTV feeds.

---

# 📸 Screenshots

Visualizing the system helps demonstrate the effectiveness of TrafficPilot AI.

### 🚦 Traffic Simulation

![Traffic Simulation](images/mod_int.png)

> 💡 **Tip:** Add additional screenshots or a short demo GIF (`README_ASSETS/demo.gif`) to showcase real-time vehicle detection and adaptive signal optimization.

---

# 🛣️ Future Roadmap

TrafficPilot AI is designed with scalability in mind. Planned enhancements include:

- 🚑 Emergency Vehicle Priority Detection
- 🚶 Pedestrian Detection & Crossing Assistance
- 🚦 Multi-Intersection Traffic Coordination
- 📡 Live CCTV Camera Integration
- ☁️ Cloud-based Traffic Monitoring Dashboard
- 📊 Real-time Traffic Analytics & Reporting
- 📱 Mobile Monitoring Application
- 🌍 Smart City Infrastructure Integration
- 🔔 Traffic Incident Detection & Alerts
- 🤖 Reinforcement Learning-based Signal Optimization
- 🛰️ Edge AI Deployment for Low-Latency Processing

---

# 🤝 Contributing

Contributions are always welcome!

If you'd like to improve TrafficPilot AI:

1. 🍴 Fork this repository.
2. 🌿 Create a new feature branch.
3. 💻 Implement your improvements.
4. ✅ Commit your changes.
5. 🚀 Push your branch.
6. 🔄 Open a Pull Request.

Please read **CONTRIBUTING.md** before contributing.

We appreciate every contribution that helps make TrafficPilot AI better.

---

# 📜 License

This project is licensed under the **MIT License**.

You are free to use, modify, and distribute this project under the terms of the MIT License.

For more details, please refer to the **LICENSE** file.

---

# 👨‍💻 Authors

| Name | Role |
|------|------|
| **Tanay Surya Vaikuntapu** | AI & Software Development |
| **S. Tulasi Prasad** | Project Mentor / Contributor |
| **Goli Jahnavi** | Project Contributor |
| **Tanay Surya Vardhan** | AI & Computer Vision |
| **Shaik Salman** | Project Contributor |

---

# 📚 Citation

If you use this project in your research, publication, or academic work, please cite it as:

```bibtex
@misc{trafficpilotai2025,
  title={TrafficPilot AI: Autonomous Traffic Management Agent using YOLOv11},
  author={Tanay Surya Vaikuntapu and S. Tulasi Prasad and Goli Jahnavi and Tanay Surya Vardhan and Shaik Salman},
  year={2025},
  howpublished={\url{https://github.com/TanaySurya-369/Adaptive-Traffic-Control-YOLOv11}}
}
```

---

# 🌟 Project Impact

TrafficPilot AI demonstrates how Artificial Intelligence and Computer Vision can improve modern traffic management systems.

Potential benefits include:

- 🚦 Smarter traffic signal control
- 🚗 Improved traffic flow
- ⏱️ Reduced congestion and waiting time
- ⛽ Lower fuel consumption
- 🌱 Reduced environmental impact
- 🏙️ Support for Smart City initiatives

---

# ⭐ Support

If you found this project useful, please consider:

- ⭐ Starring the repository
- 🍴 Forking the project
- 🐞 Reporting issues
- 💡 Suggesting new features
- 🤝 Contributing improvements

Your support motivates future development and helps improve the project for everyone.

---

# 🙏 Acknowledgements

Special thanks to the open-source community and the technologies that made this project possible.

### Frameworks & Libraries

- 🚀 Ultralytics (YOLOv11)
- 👁️ OpenCV
- 🔥 PyTorch
- 🎮 Pygame
- 🔢 NumPy

### Special Appreciation

- All contributors and reviewers
- The Computer Vision community
- The Python open-source ecosystem
- Everyone supporting AI for Smart Cities

---

# 📬 Contact

For questions, suggestions, or collaboration opportunities:

- **GitHub:** https://github.com/TanaySurya-369
- **Repository:** https://github.com/TanaySurya-369/Adaptive-Traffic-Control-YOLOv11

---

<div align="center">

## ⭐ If you like this project, don't forget to leave a Star!

### 🚦 Building Smarter Cities with Artificial Intelligence

**Made with ❤️ using Python, YOLOv11, OpenCV, PyTorch, and Pygame**

---

### Thank you for visiting this repository!

</div>
