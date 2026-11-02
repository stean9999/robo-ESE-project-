#!/usr/bin/env python3
"""
Node: goal_pose.py
Package: auto_nav
Description: Sends a single autonomous navigation goal to 'move_base' action server
             with active, feedback, and done callbacks. Directly corresponds to
             Mecharithm ROS 101 Lesson 9 (33:26 - 47:12).
"""

import math
import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from actionlib_msgs.msg import GoalStatus
from geometry_msgs.msg import Quaternion

def yaw_to_quaternion(yaw_radians):
    q = Quaternion()
    q.x = 0.0
    q.y = 0.0
    q.z = math.sin(yaw_radians / 2.0)
    q.w = math.cos(yaw_radians / 2.0)
    return q

def active_cb():
    rospy.loginfo("[CALLBACK - ACTIVE] Goal has been accepted by move_base action server.")

feedback_count = 0
def feedback_cb(feedback):
    global feedback_count
    feedback_count += 1
    if feedback_count % 15 == 0:
        pos = feedback.base_position.pose.position
        rospy.loginfo(f"[CALLBACK - FEEDBACK] Current Robot Position: x = {pos.x:.2f}, y = {pos.y:.2f}")

def done_cb(status, result):
    if status == GoalStatus.SUCCEEDED:
        rospy.loginfo("[CALLBACK - DONE] Target goal successfully REACHED!")
    elif status == GoalStatus.ABORTED:
        rospy.logerr("[CALLBACK - DONE] Goal was ABORTED by move_base planner.")
    else:
        rospy.logwarn(f"[CALLBACK - DONE] Goal finished with status code: {status}")

def send_goal(x=1.5, y=1.0, yaw=1.57):
    rospy.init_node('goal_pose_client', anonymous=False)

    x = rospy.get_param('~x', x)
    y = rospy.get_param('~y', y)
    yaw = rospy.get_param('~yaw', yaw)

    rospy.loginfo("[auto_nav] Connecting to 'move_base' action server...")
    client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
    client.wait_for_server()
    rospy.loginfo("[auto_nav] Action server connected.")

    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = "map"
    goal.target_pose.header.stamp = rospy.Time.now()
    goal.target_pose.pose.position.x = float(x)
    goal.target_pose.pose.position.y = float(y)
    goal.target_pose.pose.position.z = 0.0
    goal.target_pose.pose.orientation = yaw_to_quaternion(yaw)

    rospy.loginfo(f"[auto_nav] Sending target goal: (x={x:.2f}, y={y:.2f}, yaw={yaw:.2f} rad)...")
    client.send_goal(goal, done_cb=done_cb, active_cb=active_cb, feedback_cb=feedback_cb)

    client.wait_for_result()
    return client.get_state()

if __name__ == '__main__':
    try:
        send_goal()
    except rospy.ROSInterruptException:
        rospy.loginfo("[auto_nav] Goal pose client terminated.")

