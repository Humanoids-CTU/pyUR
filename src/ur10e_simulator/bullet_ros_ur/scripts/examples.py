#!/usr/bin/env python3

import rospy
from bullet_ros_ur.motion_interface import MoveGroupPythonInterface
from bullet_ros_ur.robot_kinematics_interface import ForwardKinematics, InverseKinematics
import numpy as np
from geometry_msgs.msg import PoseStamped, WrenchStamped
from std_msgs.msg import Float64MultiArray
from controller_manager_msgs.srv import SwitchController, SwitchControllerRequest
from bullet_ros_ur.srv import grip, gripRequest


if __name__ == "__main__":
    rospy.init_node("examples_node")

    """
    Connect to Motion Interface with group 'manipulator'
        - group 'manipulator' is from base_link to gripper_link frame (in the middle of solid part of the gripper)
        - there is also group 'arm' going to the flange of the robot (tool0 link)
        - other groups can be defined in universal_robot/ur10e_moveit_config/config/ur10e_rg6.srdf
    """

    MoveGroupArm = MoveGroupPythonInterface("manipulator")

    """
    Just info message
    """
    rospy.loginfo("Starting ")

    """
    Get current end-effector and get its pose:
    """
    rospy.loginfo(f"Current end-effector is {MoveGroupArm.eef_link}")
    rospy.loginfo(f"Pose of the end-effector is: {MoveGroupArm.get_ee_pose()}")

    """
    Move the robot 5cm up from its current position
    """
    p = MoveGroupArm.get_ee_pose()
    p.position.z -= 0.1
    MoveGroupArm.go_to_pose(p, wait=True)  # True here is to block the program until completion of the movement.

    """
    Get current joint state of the robot:
    """
    rospy.loginfo(f"Joint state is: {MoveGroupArm.get_current_state()}")

    """
    Move joint_0 25 degrees from current position
    """
    p = MoveGroupArm.get_current_state()
    p[0] += np.deg2rad(25)
    MoveGroupArm.go_to_joint_position(p)

    """
    Open the gripper
    """
    rospy.loginfo("Opening gripper")
    MoveGroupArm.open_gripper()

    """
    Close the gripper
    """
    rospy.loginfo("Closing gripper")
    MoveGroupArm.close_gripper()

    """
    The previous command corresponds to calling /ur_hardware_interface/grip service with width 150mm and force 120N
    for opening and 0mm and 120N for closing
    The service also support other widths (0-150) and forces (0-120).
    To call it
    """
    grip_service = rospy.ServiceProxy("/robot/ur_hardware_interface/grip", grip)
    request = gripRequest()
    request.width = 100
    request.force = 30

    rospy.loginfo(f"Gripper moved successfully: {grip_service.call(request)}")

    """
    Get inverse kinematics without movement
    """
    # Create pose request
    pose_current = MoveGroupArm.get_ee_pose()

    ps = PoseStamped()
    ps.header.stamp = rospy.Time.now()
    ps.header.frame_id = "base_link"
    ps.pose = pose_current

    ik = InverseKinematics()

    result = ik.getIK(group_name="manipulator", ik_link_name="gripper_link", pose=ps, avoid_collisions=True, timeout=0.1)
    rospy.loginfo(f"The IK solution is: {result}")

    """VELOCITY CONTROL"""
    rospy.loginfo("Velocity control")
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
    msg.data = [-0.1, 0.0, 0.0, 0.0, 0.0, 0.0]  # 0.1 rad/s in joint_0
    pub.publish(msg)

    rospy.sleep(5) # do the movement for some time

    msg.data = [0, 0, 0, 0, 0, 0]  # stop the motion by calling 0 in all
    pub.publish(msg)
    rospy.sleep(1)


    """
    CARTESIAN MOTION CONTROLLER
    Move the robot 10 cm upward by publishing a target pose to /robot/target_frame.
    The CartesianMotionController drives the joints so that the end-effector
    tracks the published PoseStamped continuously.
    """
    rospy.loginfo("Cartesian controller")
    # req = SwitchControllerRequest()
    req.start_controllers = ["cartesian_motion_controller"]
    req.stop_controllers = ["joint_group_vel_controller"]
    switch_srv.call(req)

    target_frame_pub = rospy.Publisher("/robot/target_frame", PoseStamped, queue_size=1, latch=True)
    while target_frame_pub.get_num_connections() == 0 and not rospy.is_shutdown():
        rospy.sleep(0.1)  # let the publisher register

    ps = PoseStamped()
    ps.header.frame_id = "base_link"
    ps.header.stamp = rospy.Time.now()
    ps.pose = MoveGroupArm.get_ee_pose()

    # NOTE
    # This is just to show the control. In the real scenario you should in most case use smooth trajectory instead of big jumps like this
    ps.pose.position.y += 0.2 # go 0.2 forward
    target_frame_pub.publish(ps)
    rospy.sleep(5.0) # wait some time

    ps.pose.position.y -= 0.2  # return backward
    target_frame_pub.publish(ps)

    rospy.sleep(5.0)


    """
    CARTESIAN FORCE CONTROLLER
    Apply a 5 N downward force by publishing a target wrench to /robot/target_wrench.
    The CartesianForceController generates joint commands so that the end-effector
    applies the desired force/torque (it reads the actual wrench from /robot/wrench).
    """
    rospy.loginfo("Force controller")
    req.start_controllers = ["cartesian_force_controller"]
    req.stop_controllers = ["cartesian_motion_controller"]
    switch_srv.call(req)

    target_wrench_pub = rospy.Publisher("/robot/target_wrench", WrenchStamped, queue_size=1, latch=True)
    while target_wrench_pub.get_num_connections() == 0 and not rospy.is_shutdown():
        rospy.sleep(0.1)  # let the publisher register

    wrench_msg = WrenchStamped()
    wrench_msg.header.frame_id = "base_link"
    wrench_msg.header.stamp = rospy.Time.now()
    wrench_msg.wrench.force.z = 100.0  # push forward by the force of 100N
    target_wrench_pub.publish(wrench_msg)
    #
    rospy.sleep(5.0)
    #
    wrench_msg.wrench.force.z = 0  # stop pushing
    target_wrench_pub.publish(wrench_msg)
    rospy.sleep(3.0)


    """
    CARTESIAN COMPLIANCE CONTROLLER
    The compliance controller combines both a pose target and a feed-forward wrench.
    It subscribes to /robot/target_frame (PoseStamped) and /robot/target_wrench (WrenchStamped).
    The robot tracks the target pose while remaining compliant to external forces.
    """
    rospy.loginfo("Compliance controller")
    req.start_controllers = ["cartesian_compliance_controller"]
    req.stop_controllers = ["cartesian_force_controller"]
    switch_srv.call(req)

    # target_frame_pub and target_wrench_pub are reused from above
    rospy.sleep(0.5)

    ps = PoseStamped()
    ps.header.frame_id = "base_link"
    ps.header.stamp = rospy.Time.now()
    ps.pose = MoveGroupArm.get_ee_pose()
    ps.pose.position.x -= 0.1  # 5 cm to the right
    target_frame_pub.publish(ps)

    wrench_msg.wrench.force.x = 2.0  # 2 N feed-forward in Y
    target_wrench_pub.publish(wrench_msg)

    rospy.sleep(4.0)

    ps.pose.position.x += 0.1  # return to original position
    wrench_msg.wrench.force.x = 0.0
    target_frame_pub.publish(ps)
    target_wrench_pub.publish(wrench_msg)

    rospy.sleep(4.0)

    req.start_controllers = ["scaled_pos_joint_traj_controller"]
    req.stop_controllers = ["cartesian_compliance_controller"]
    switch_srv.call(req)

    """
    INTERACTIVE MARKER (drag-and-drop in RViz)
    The motion_control_handle controller is started automatically by simulation.launch.
    It places an orange sphere at the current end-effector position in RViz.

    To use it:
      1. Switch to cartesian_motion_controller (or cartesian_compliance_controller)
         as shown above.
      2. run motion_control_handle (it is loaded but not running by default, as it is interfering with moving the robot through topics)
      3. In RViz, drag the orange sphere along any axis or rotate it –
         the robot follows in real time.
      4. Reset the marker to the current EEF pose at any time:
             rosservice call /moving_target/reset
    """

