#!/usr/bin/env python3
"""
Node: initial_pose.py
Package: auto_nav
Description: Programmatically publishes the initial robot pose to the '/initialpose'
             topic so AMCL (Adaptive Monte Carlo Localization) can estimate the robot's
             location on the map without requiring manual '2D Pose Estimate' in RViz.
"""

import math
import rospy
from geometry_msgs.msg import PoseWithCovarianceStamped, Quaternion

def yaw_to_quaternion(yaw_radians):
    """
    Converts a planar yaw angle (rotation around Z axis) into a ROS Quaternion message.
    Formula:
        qx = 0.0
        qy = 0.0
        qz = sin(yaw / 2)
        qw = cos(yaw / 2)
    """
    q = Quaternion()
    q.x = 0.0
    q.y = 0.0
    q.z = math.sin(yaw_radians / 2.0)
    q.w = math.cos(yaw_radians / 2.0)
    return q

def publish_initial_pose(x=-2.0, y=-0.5, yaw=0.0):
    """
    Creates and broadcasts a PoseWithCovarianceStamped message to '/initialpose'.
    
    Args:
        x (float): Initial X position in map frame (meters). Standard TurtleBot3 world default is -2.0.
        y (float): Initial Y position in map frame (meters). Standard TurtleBot3 world default is -0.5.
        yaw (float): Initial orientation angle in radians (0.0 rad = pointing along +X axis).
    """
    # 1. Initialize ROS node
    rospy.init_node('initial_pose_publisher', anonymous=True)
    
    # Allow parameters to override initial coordinates from roslaunch or CLI
    x = rospy.get_param('~x', x)
    y = rospy.get_param('~y', y)
    yaw = rospy.get_param('~yaw', yaw)

    # 2. Setup publisher to '/initialpose'
    pub = rospy.Publisher('/initialpose', PoseWithCovarianceStamped, queue_size=10)
    
    rospy.loginfo("[auto_nav] Initializing pose publisher...")
    rospy.loginfo(f"[auto_nav] Target Initial Pose -> X: {x:.2f} m, Y: {y:.2f} m, Yaw: {yaw:.2f} rad")

    # 3. Wait until AMCL has subscribed to avoid ROS topic race condition
    rate = rospy.Rate(5)  # 5 Hz
    timeout_counter = 0
    max_wait_seconds = 10.0
    
    rospy.loginfo("[auto_nav] Waiting for AMCL subscriber to connect to '/initialpose'...")
    while pub.get_num_connections() == 0 and not rospy.is_shutdown():
        if timeout_counter >= (max_wait_seconds * 5):
            rospy.logwarn("[auto_nav] Warning: No active subscriber detected on '/initialpose' after 10s. Publishing anyway...")
            break
        rate.sleep()
        timeout_counter += 1

    # 4. Construct the PoseWithCovarianceStamped message
    pose_msg = PoseWithCovarianceStamped()
    pose_msg.header.stamp = rospy.Time.now()
    pose_msg.header.frame_id = "map"  # AMCL requires map frame coordinates

    # Position
    pose_msg.pose.pose.position.x = float(x)
    pose_msg.pose.pose.position.y = float(y)
    pose_msg.pose.pose.position.z = 0.0

    # Orientation (convert planar yaw to quaternion)
    pose_msg.pose.pose.orientation = yaw_to_quaternion(yaw)

    # 5. Define the 6x6 Covariance matrix (flattened to 36 elements)
    # Order: [x, y, z, roll, pitch, yaw]
    # Covariance diagonals represent uncertainty variance:
    #   Index 0: Var(X) = 0.25 (0.5m std dev)
    #   Index 7: Var(Y) = 0.25 (0.5m std dev)
    #   Index 35: Var(Yaw) = ~0.0685 rad^2 (approx 15 deg std dev)
    covariance = [0.0] * 36
    covariance[0] = 0.25                      # Var(x)
    covariance[7] = 0.25                      # Var(y)
    covariance[14] = 0.0                      # Var(z)
    covariance[21] = 0.0                      # Var(roll)
    covariance[28] = 0.0                      # Var(pitch)
    covariance[35] = (math.pi / 12.0) ** 2    # Var(yaw) = (15 degrees)^2 in rads

    pose_msg.pose.covariance = covariance

    # 6. Publish in a short burst to ensure AMCL particle cloud initializes reliably
    rospy.loginfo("[auto_nav] Broadcasting initial pose to AMCL...")
    for i in range(5):
        if rospy.is_shutdown():
            break
        pose_msg.header.stamp = rospy.Time.now()
        pub.publish(pose_msg)
        rospy.sleep(0.3)

    rospy.loginfo("=================================================================")
    rospy.loginfo("[auto_nav] Initial pose successfully published! AMCL particles reset.")
    rospy.loginfo("=================================================================")

if __name__ == '__main__':
    try:
        publish_initial_pose()
    except rospy.ROSInterruptException:
        rospy.loginfo("[auto_nav] Initial pose publisher terminated by user.")

