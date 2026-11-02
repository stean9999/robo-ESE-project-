#!/bin/bash
# ==============================================================================
# Master Automated Launcher: TurtleBot3 Autonomous Navigation
# Runs the entire pipeline in 1 command without needing 4 manual terminals!
# ==============================================================================

# Ensure script stops on interrupt
trap 'echo -e "\n[auto_nav] Stopping all background processes..."; kill $(jobs -p) 2>/dev/null; exit' SIGINT SIGTERM

export TURTLEBOT3_MODEL=burger

# Determine workspace directory
WS_DIR=~/catkin_ws
if [ -f "$WS_DIR/devel/setup.bash" ]; then
    source "$WS_DIR/devel/setup.bash"
else
    source /opt/ros/$ROS_DISTRO/setup.bash 2>/dev/null
fi

echo "=================================================================="
echo "  TURTLEBOT3 1-CLICK AUTONOMOUS WAREHOUSE NAVIGATION LAUNCHER"
echo "=================================================================="

echo -e "\n[STEP 1/4] Launching Gazebo TurtleBot3 World..."
roslaunch turtlebot3_gazebo turtlebot3_world.launch &
GAZEBO_PID=$!

echo "[INFO] Waiting 8 seconds for Gazebo physics engine to initialize..."
sleep 8

echo -e "\n[STEP 2/4] Launching AMCL Localization, move_base & RViz..."
roslaunch turtlebot3_navigation turtlebot3_navigation.launch &
NAV_PID=$!

echo "[INFO] Waiting 10 seconds for move_base Action Server & AMCL to become ready..."
sleep 10

echo -e "\n[STEP 3/4] Publishing Programmatic Initial Pose (/initialpose)..."
rosrun auto_nav initial_pose.py

echo "[INFO] Pausing 2 seconds for AMCL particle cloud convergence..."
sleep 2

echo -e "\n[STEP 4/4] Starting Multi-Station Warehouse Mission..."
rosrun auto_nav waypoint_navigator.py

echo -e "\n=================================================================="
echo "  MISSION COMPLETED SUCCESSFULLY!"
echo "  Press Ctrl+C to close Gazebo, RViz, and exit cleanly."
echo "=================================================================="

wait

