#!/usr/bin/env python3
"""
Node: waypoint_navigator.py
Package: auto_nav
Description: Action client communicating with 'move_base' action server using actionlib.
             Executes sequential warehouse navigation across multiple stations:
             1. Loading Dock
             2. Shelf Area A
             3. Sorting Desk
             4. Charging Base
             Features active, feedback, and done callbacks, state handling,
             and simulated 2-second dwell time per waypoint.
"""

import math
import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from actionlib_msgs.msg import GoalStatus
from geometry_msgs.msg import Quaternion

class WaypointNavigator:
    def __init__(self):
        # 1. Initialize node
        rospy.init_node('waypoint_navigator', anonymous=False)
        rospy.on_shutdown(self.shutdown_handler)

        # 2. Setup SimpleActionClient for 'move_base'
        rospy.loginfo("[auto_nav] Connecting to 'move_base' action server...")
        self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        
        # Wait until action server is active
        server_connected = self.client.wait_for_server(timeout=rospy.Duration(60.0))
        if not server_connected:
            rospy.logerr("[auto_nav] Could not connect to 'move_base' server. Ensure navigation stack is running!")
            rospy.signal_shutdown("Action server timeout")
            return

        rospy.loginfo("[auto_nav] Connected to 'move_base' action server successfully.")

        # 3. Define Warehouse Waypoints
        # Format: (name, x [m], y [m], yaw [rad])
        # Coordinates are chosen for clear paths in standard turtlebot3_world
        self.waypoints = [
            {
                "name": "Loading Dock",
                "x": -1.8,
                "y": -0.5,
                "yaw": 0.0,
                "task": "Loading warehouse pallets..."
            },
            {
                "name": "Shelf Area A",
                "x": 0.5,
                "y": 1.5,
                "yaw": 1.57,
                "task": "Placing inventory on rack A3..."
            },
            {
                "name": "Sorting Desk",
                "x": 1.8,
                "y": -1.0,
                "yaw": 3.14,
                "task": "Scanning barcode items..."
            },
            {
                "name": "Charging Base",
                "x": -0.5,
                "y": 0.5,
                "yaw": -1.57,
                "task": "Docking and replenishing battery..."
            }
        ]

        self.current_goal_name = ""
        self.feedback_counter = 0

    def yaw_to_quaternion(self, yaw_radians):
        """Converts yaw (heading angle in radians) into a geometry_msgs Quaternion."""
        q = Quaternion()
        q.x = 0.0
        q.y = 0.0
        q.z = math.sin(yaw_radians / 2.0)
        q.w = math.cos(yaw_radians / 2.0)
        return q

    def create_move_base_goal(self, x, y, yaw):
        """Builds a standard MoveBaseGoal message with target coordinates in 'map' frame."""
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()

        # Goal position
        goal.target_pose.pose.position.x = float(x)
        goal.target_pose.pose.position.y = float(y)
        goal.target_pose.pose.position.z = 0.0

        # Goal orientation
        goal.target_pose.pose.orientation = self.yaw_to_quaternion(yaw)

        return goal

    # ==========================
    # Action Client Callbacks
    # ==========================
    def active_callback(self):
        """Callback invoked when the goal is accepted and begins processing by move_base."""
        rospy.loginfo(f"[CALLBACK - ACTIVE] Goal '{self.current_goal_name}' has been accepted by move_base.")

    def feedback_callback(self, feedback):
        """Callback invoked periodically by move_base during trajectory execution."""
        # Throttle feedback logs to avoid flooding terminal
        self.feedback_counter += 1
        if self.feedback_counter % 20 == 0:
            current_x = feedback.base_position.pose.position.x
            current_y = feedback.base_position.pose.position.y
            rospy.loginfo(f"[CALLBACK - FEEDBACK] En route to '{self.current_goal_name}' | Robot Pose: (x={current_x:.2f}, y={current_y:.2f})")

    def done_callback(self, status, result):
        """Callback invoked when goal execution completes, aborts, or is preempted."""
        status_descriptions = {
            GoalStatus.PENDING: "PENDING (Goal not yet processed)",
            GoalStatus.ACTIVE: "ACTIVE (Goal is currently processing)",
            GoalStatus.PREEMPTED: "PREEMPTED (Goal canceled by user/new goal)",
            GoalStatus.SUCCEEDED: "SUCCEEDED (Robot arrived at target successfully)",
            GoalStatus.ABORTED: "ABORTED (move_base failed to find or follow path)",
            GoalStatus.REJECTED: "REJECTED (Goal rejected by action server)",
            GoalStatus.RECALLED: "RECALLED (Goal cancelled before processing started)"
        }
        status_text = status_descriptions.get(status, f"UNKNOWN STATUS CODE: {status}")
        rospy.loginfo(f"[CALLBACK - DONE] Goal '{self.current_goal_name}' finished with status: {status_text}")

    # ==========================
    # Main Navigation Loop
    # ==========================
    def start_mission(self):
        """Iterates sequentially through all warehouse waypoints."""
        total_waypoints = len(self.waypoints)
        rospy.loginfo("=================================================================")
        rospy.loginfo(f"[auto_nav] Starting Autonomous Warehouse Navigation ({total_waypoints} stations)")
        rospy.loginfo("=================================================================")

        for idx, wp in enumerate(self.waypoints, start=1):
            if rospy.is_shutdown():
                rospy.logwarn("[auto_nav] Navigation interrupted before completion.")
                break

            self.current_goal_name = wp["name"]
            self.feedback_counter = 0

            rospy.loginfo(f"\n---> [STATION {idx}/{total_waypoints}]: Traveling to '{wp['name']}'")
            rospy.loginfo(f"     Coordinates: (x: {wp['x']:.2f}, y: {wp['y']:.2f}, yaw: {wp['yaw']:.2f} rad)")

            # Generate goal message
            goal_msg = self.create_move_base_goal(wp["x"], wp["y"], wp["yaw"])

            # Send goal to move_base action server with registered callbacks
            self.client.send_goal(
                goal_msg,
                done_cb=self.done_callback,
                active_cb=self.active_callback,
                feedback_cb=self.feedback_callback
            )

            # Block until result is received
            self.client.wait_for_result()
            state = self.client.get_state()

            if state == GoalStatus.SUCCEEDED:
                rospy.loginfo(f"[SUCCESS] Robot successfully reached '{wp['name']}'!")
                rospy.loginfo(f"[OPERATION] {wp['task']}")
                rospy.loginfo("[OPERATION] Pausing for 2.0 seconds at station...")
                rospy.sleep(2.0)  # Simulated loading/unloading delay
            elif state == GoalStatus.ABORTED:
                rospy.logerr(f"[ABORTED] Path to '{wp['name']}' is blocked or unreachable by global/local planner.")
                rospy.logwarn("[RECOVERY] Skipping to next station...")
            elif state == GoalStatus.PREEMPTED:
                rospy.logwarn(f"[PREEMPTED] Goal '{wp['name']}' was preempted.")
                break
            else:
                rospy.logwarn(f"[WARNING] Goal '{wp['name']}' terminated with state: {state}")

        rospy.loginfo("\n=================================================================")
        rospy.loginfo("[auto_nav] Autonomous Warehouse Navigation Mission Completed!")
        rospy.loginfo("=================================================================")

    def shutdown_handler(self):
        """Cancels all active goals safely if node is stopped (e.g., Ctrl+C)."""
        rospy.logwarn("[auto_nav] Shutdown requested. Cancelling all active move_base goals...")
        self.client.cancel_all_goals()

if __name__ == '__main__':
    try:
        navigator = WaypointNavigator()
        navigator.start_mission()
    except rospy.ROSInterruptException:
        rospy.loginfo("[auto_nav] Waypoint navigation terminated cleanly.")

