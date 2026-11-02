# Auto Nav - Autonomous TurtleBot3 Navigation Package (ROS 1)

This repository contains the complete **`auto_nav`** ROS 1 package for fully automated TurtleBot3 navigation without manual RViz GUI intervention (no manual *2D Pose Estimate* or *2D Nav Goal*).

Designed for Robotics Lab End-Semester Exams (LAB ESE) and based on **Mecharithm ROS 101 Lesson 9**.

---

## 1. Package Architecture

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

## 2. Directory Structure

```
auto_nav/
├── CMakeLists.txt
├── package.xml
├── launch/
│   └── auto_nav_mission.launch
├── scripts/
│   ├── initial_pose.py         # Node 1: Programmatic AMCL localization initializer
│   ├── goal_pose.py            # Single goal action client (from Lesson 9)
│   └── waypoint_navigator.py   # Node 2: Multi-waypoint warehouse mission planner
└── README.md
```

---

## 3. Prerequisites & Installation

### A. Dependencies
Ensure TurtleBot3 and navigation packages are installed (example for **ROS Noetic**):

```bash
sudo apt update
sudo apt install -y \
  ros-noetic-turtlebot3 \
  ros-noetic-turtlebot3-msgs \
  ros-noetic-turtlebot3-simulations \
  ros-noetic-navigation
```
*(If using ROS Melodic, replace `noetic` with `melodic`)*

### B. Workspace Setup
Copy or clone the `auto_nav` folder into your catkin workspace source directory:

```bash
# If your workspace is ~/catkin_ws:
mkdir -p ~/catkin_ws/src
cp -r /path/to/auto_nav ~/catkin_ws/src/

# Make python scripts executable:
cd ~/catkin_ws/src/auto_nav/scripts
chmod +x initial_pose.py goal_pose.py waypoint_navigator.py

# Build package:
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

---

## 4. Complete Terminal Run Procedure

Open **4 separate terminals** (or use tmux/terminator). In **every terminal**, remember to export the TurtleBot3 model and source your catkin workspace.

### **Terminal 1: Launch Gazebo Simulation**
Spawns the TurtleBot3 inside the simulated world.
```bash
export TURTLEBOT3_MODEL=burger
source ~/catkin_ws/devel/setup.bash
roslaunch turtlebot3_gazebo turtlebot3_world.launch
```

### **Terminal 2: Launch Navigation Stack (AMCL + move_base + RViz)**
Launches map server, AMCL localization node, move_base path planner, and RViz.
```bash
export TURTLEBOT3_MODEL=burger
source ~/catkin_ws/devel/setup.bash
roslaunch turtlebot3_navigation turtlebot3_navigation.launch
```
> *Observe RViz*: Notice that green AMCL particle cloud is initially unaligned and dispersed.

### **Terminal 3: Initialize Robot Pose (Programmatically)**
Executes `initial_pose.py` to broadcast coordinates to `/initialpose`.
```bash
source ~/catkin_ws/devel/setup.bash
rosrun auto_nav initial_pose.py
```
> *Result*: AMCL converges immediately. The robot footprint in RViz locks exactly onto the Gazebo spawn point. No manual "2D Pose Estimate" clicking needed!

### **Terminal 4: Start Autonomous Waypoint Mission**
Executes the warehouse mission across all 4 stations with 2-second dwell delays:
```bash
source ~/catkin_ws/devel/setup.bash
rosrun auto_nav waypoint_navigator.py
```

---

## 5. Warehouse Waypoint Locations

| Station | Location Name | X (m) | Y (m) | Yaw (rad) | Simulated Operation |
|:---:|:---|:---:|:---:|:---:|:---|
| 1 | **Loading Dock** | -1.80 | -0.50 | 0.00 | Pallet loading |
| 2 | **Shelf Area A** | 0.50 | 1.50 | 1.57 | Inventory storage |
| 3 | **Sorting Desk** | 1.80 | -1.00 | 3.14 | Barcode scanning |
| 4 | **Charging Base** | -0.50 | 0.50 | -1.57 | Battery docking |

---

## 6. Key ROS Concepts for LAB Viva / ESE

1. **Why is `PoseWithCovarianceStamped` required for `/initialpose`?**
   - AMCL is a probabilistic particle filter. It needs an initial estimate along with **uncertainty (covariance)** to seed the random particle cloud. 
   - `covariance[0] = 0.25` ($\sigma = 0.5\text{ m}$ for X), `covariance[7] = 0.25` ($\sigma = 0.5\text{ m}$ for Y), and `covariance[35] = (\pi/12)^2 \approx 0.0685\text{ rad}^2$ ($\sigma \approx 15^\circ$ for Yaw).

2. **Why ActionLib instead of ROS Topics/Services for Navigation?**
   - Navigation is a long-running, non-instantaneous task.
   - Topics are "fire-and-forget" with no acknowledgment.
   - Services block the caller and cannot provide continuous feedback or mid-course cancellation.
   - **ActionLib** supports **asynchronous execution**, continuous feedback callbacks (`feedback_cb`), goal preemption/cancellation, and terminal status notification (`done_cb`).

3. **Why did we include a subscriber check before publishing in `initial_pose.py`?**
   - In ROS, topic publishers take a brief moment to discover and establish a TCP connection with subscribers. Publishing immediately upon node creation causes message dropping (publisher race condition).

