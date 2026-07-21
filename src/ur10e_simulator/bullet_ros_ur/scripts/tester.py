#!/usr/bin/env python3

import rospy
from bullet_ros_ur.motion_interface import MoveGroupPythonInterface
from bullet_ros_ur.robot_kinematics_interface import ForwardKinematics, InverseKinematics
import numpy as np
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float64MultiArray
from controller_manager_msgs.srv import SwitchController, SwitchControllerRequest
from bullet_ros_ur.srv import grip, gripRequest


if __name__ == "__main__":
    rospy.init_node("examples_node")

    MoveGroupArm = MoveGroupPythonInterface("manipulator")


    """VELOCITY CONTROL"""
    # Switch to velocity control
    switch_srv = rospy.ServiceProxy("/robot/controller_manager/switch_controller", SwitchController)
    switch_srv.wait_for_service()
    req = SwitchControllerRequest()
    req.start_controllers = ["joint_group_vel_controller"]
    req.stop_controllers = ["scaled_pos_joint_traj_controller"]
    req.strictness = 2
    req.start_asap = False
    switch_srv.call(req)

    # Publish velocity commands
    pub = rospy.Publisher("/joint_group_vel_controller/command", Float64MultiArray, queue_size=1, latch=True)
    msg = Float64MultiArray()
    msg.data = [0, -1, 0.0, 0.0, 0.0, 0.0]  # 0.1 rad/s in joint_0
    pub.publish(msg)

    rospy.sleep(2) # do the movement for some time

    msg.data = [0, 1, 0, 0, 0, 0]  # stop the motion by calling 0 in all
    pub.publish(msg)

    rospy.sleep(2) # do the movement for some time

    msg.data = [0, 0, 0, 0, 0, 0]  # stop the motion by calling 0 in all
    pub.publish(msg)

