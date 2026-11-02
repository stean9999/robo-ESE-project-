# 🐢 TurtleBot3 Autonomous Warehouse Navigation (ROS 1 auto_nav)

[![ROS 1](https://img.shields.io/badge/ROS-Noetic%20%7C%20Melodic-blue.svg)](http://wiki.ros.org/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Ubuntu%20%7C%20Windows-lightgrey.svg)](https://ubuntu.com/)

An end-to-end **programmatic autonomous navigation system** for TurtleBot3 using ROS 1, designed to eliminate all manual GUI intervention in RViz (no manual *2D Pose Estimate* or *2D Nav Goal*).

Includes the complete **`auto_nav`** ROS 1 package, an **interactive 2D simulator** that runs directly on Windows/Browser, and a comprehensive **Lab ESE Exam & Viva Preparation Guide**.

---

## 📌 Project Motivation

In standard ROS tutorials, robot navigation requires a human operator to manually click buttons using a mouse in RViz:
1. Click **"2D Pose Estimate"** to set the robot's starting position.
2. Click **"2D Nav Goal"** for every single waypoint.

In real-world automated logistics (e.g., Amazon, Flipkart, DHL fulfillment centers) with hundreds of Autonomous Mobile Robots (AMRs), manual mouse clicking is impossible.

**This project delivers 100% Zero-GUI Autonomy:**
* **`initial_pose.py`**: Broadcasts `PoseWithCovarianceStamped` directly to the `/initialpose` topic with proper covariance diagonal values, locking AMCL particles automatically on startup.
* **`waypoint_navigator.py`**: An Action Client that connects to the `move_base` Action Server (`MoveBaseAction`) to sequentially drive the robot through 4 warehouse stations with a 2-second dwell delay for loading/unloading operations.

---

## 🏗️ System Architecture

```
                  +----------------------------------------------+
                  |               Gazebo Simulator              |
                  |     (TurtleBot3 World / Odometry / Laser)    |
                  +----------------------+-----------------------+
                                         | /odom, /scan
                                         v
+------------------------+        +---------------+        +----------------------+
|    initial_pose.py     | ------>|  amcl (node)  |------->|      move_base       |
|  (Initial Pose Lock)   |        | (Localization)|        |   (Global & Local    |
| /initialpose (cov diag)|        +---------------+        |     Planners)        |
+------------------------+                                 +-----------^----------+
                                                                       |
+----------------------------------------------------------------------+ MoveBaseAction
|  waypoint_navigator.py (Action Client)                               | (Goals, Status,
|  - Loading Dock -> Shelf Area A -> Sorting Desk -> Charging Base     |  Feedback)
+----------------------------------------------------------------------+
```

---

## 🏬 Warehouse Waypoints & Tasks

| Station | Station Name | X (m) | Y (m) | Yaw (rad) | Simulated Task (2s Dwell Time) |
|:---:|:---|:---:|:---:|:---:|:---|
| 1 | **Loading Dock** | -1.80 | -0.50 | 0.00 | Loading warehouse pallets onto robot |
| 2 | **Shelf Area A** | 0.50 | 1.50 | 1.57 | Storing items into warehouse rack shelf A3 |
| 3 | **Sorting Desk** | 1.80 | -1.00 | 3.14 | Scanning parcel barcodes & inspection |
| 4 | **Charging Base** | -0.50 | 0.50 | -1.57 | Docking to replenish battery (Finish) |

---

## 📁 Repository Structure

```
.
├── auto_nav/                                      # Official ROS 1 Catkin Package
│   ├── CMakeLists.txt                             # Catkin build configuration
│   ├── package.xml                                # Package metadata & dependencies
│   ├── README.md                                  # Package level guide
│   ├── launch/
│   │   └── auto_nav_mission.launch               # Roslaunch file
│   └── scripts/
│       ├── initial_pose.py                        # Node 1: Programmatic AMCL localization
│       ├── goal_pose.py                           # Single goal Action Client (Lesson 9)
│       ├── waypoint_navigator.py                  # Node 2: Multi-waypoint warehouse mission
│       └── run_all.sh                             # 1-Click Ubuntu master runner
├── turtlebot3_simulator.py                        # Standalone Python 2D GUI Simulator
├── turtlebot3_simulator.html                      # Standalone Web Browser Simulator
├── run_simulator.bat                              # 1-Click Windows desktop launcher
├── TurtleBot3_Autonomous_Navigation_Preparation_Guide.pdf # Exam & Viva Preparation Guide (Hinglish)
├── generate_prep_pdf.py                           # PDF generator script
└── README.md
```

---

## 🚀 How to Run

### Method 1: On Ubuntu Linux (ROS 1 Noetic / Melodic)

1. **Copy package to your catkin workspace:**
   ```bash
   cp -r auto_nav ~/catkin_ws/src/
   cd ~/catkin_ws
   catkin_make
   source devel/setup.bash
   ```

2. **Grant executable permissions:**
   ```bash
   chmod +x ~/catkin_ws/src/auto_nav/scripts/*.py
   chmod +x ~/catkin_ws/src/auto_nav/scripts/*.sh
   ```

3. **Run 1-Click Automated Pipeline:**
   ```bash
   cd ~/catkin_ws/src/auto_nav/scripts
   ./run_all.sh
   ```
   *(Or launch manually across 4 terminals as described in [`auto_nav/README.md`](auto_nav/README.md))*

---

### Method 2: On Windows (No Linux or ROS installation required)

* **Option A (Python GUI App):** Double-click [`run_simulator.bat`](run_simulator.bat) or run:
  ```powershell
  python turtlebot3_simulator.py
  ```
* **Option B (Web Browser):** Double-click [`turtlebot3_simulator.html`](turtlebot3_simulator.html) to run the simulation directly in Chrome or Edge!

---

## 📖 Exam & Viva Preparation Guide

A complete 6-page preparation guide is provided in:
📄 [**`TurtleBot3_Autonomous_Navigation_Preparation_Guide.pdf`**](TurtleBot3_Autonomous_Navigation_Preparation_Guide.pdf)

Includes:
* System architecture & component roles explained in simple Hinglish.
* Covariance matrix breakdown (36 values) & fixing ROS race conditions.
* ActionLib lifecycle: `active_cb`, `feedback_cb`, `done_cb`.
* Top 15 Lab Viva & Theory questions with model answers.
* 60-second viva presentation script for teachers/evaluators.

---

## 📜 License
This project is open-sourced under the MIT License.

