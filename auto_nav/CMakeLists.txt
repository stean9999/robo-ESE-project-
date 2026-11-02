cmake_minimum_required(VERSION 3.0.2)
project(auto_nav)

## Compile as C++11 or C++14 if any C++ nodes are added in future
add_compile_options(-std=c++14)

## Find catkin macros and libraries
find_package(catkin REQUIRED COMPONENTS
  rospy
  actionlib
  geometry_msgs
  nav_msgs
  move_base_msgs
  tf
)

## Catkin package configuration
catkin_package(
  CATKIN_DEPENDS
    rospy
    actionlib
    geometry_msgs
    nav_msgs
    move_base_msgs
    tf
)

## Specify include directories
include_directories(
  ${catkin_INCLUDE_DIRS}
)

## Mark executable Python scripts for installation
catkin_install_python(PROGRAMS
  scripts/initial_pose.py
  scripts/goal_pose.py
  scripts/waypoint_navigator.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
