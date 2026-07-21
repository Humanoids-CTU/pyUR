#!/usr/bin/env python3
import time
import rospy
from bullet_ros_ur.srv import grip, gripResponse, initGrip, initGripRequest
import numpy as np
from sensor_msgs.msg import JointState


class Gripper:
    def __init__(self):
        # Initialize the grip service
        self.grip_service = rospy.Service("/robot/ur_hardware_interface/grip", grip, self.grip)
        self.init_grip_service = rospy.ServiceProxy("/robot/ur_hardware_interface/init_grip", initGrip)
        self.js_sub = rospy.Subscriber("/joint_states", JointState, self.js_callback)
        self.MAX_WIDTH = 150
        self.MAX_FORCE = 180
        self.tolerance = 0.001  # tolerance for the gripper to be considered closed
        self.js = None

    def js_callback(self, msg):
        """
        Callback for the joint states subscriber

        :param msg: JointState message
        :type msg: sensor_msgs.msg.JointState
        """
        self.js = msg.position[msg.name.index("finger_joint")]

    def grip(self, request):
        """
        Grip request callback

        :param request: request to close/open the gripper
        :type request: bullet_ros_ur/srv/gripRequest
        :return:
        :rtype:
        """
        if not (0 <= request.width <= self.MAX_WIDTH):
            rospy.logerr("Width must be between 0-150")
            out = gripResponse()
            out.success = False
            return out

        if not (0 < request.force <= self.MAX_FORCE):
            rospy.logerr("Force must be between 0-180")
            out = gripResponse()
            out.success = False
            return out

        setpoint = self.init_grip_service(initGripRequest(width=request.width, force=request.force)).setpoint
        rospy.sleep(0.01)

        num_refs = 10
        last_refs = -99*np.ones(num_refs)
        ref_id = 0
        # wait until the gripper is closed
        while not rospy.is_shutdown():

            if np.abs(self.js - setpoint) <= self.tolerance:
                self.init_grip_service(initGripRequest(width=-1, force=0))  # stop the gripper
                break
            if last_refs[0] != -99 and np.allclose(last_refs, self.js, atol=self.tolerance):
                rospy.logwarn("Gripper is not moving, stopping it")
                self.init_grip_service(initGripRequest(width=-1, force=0))  # stop the gripper
                break
            last_refs[ref_id] = self.js
            ref_id = (ref_id + 1) % num_refs
            rospy.sleep(0.005)

        out = gripResponse()
        out.success = True
        return out

if __name__ == "__main__":
    rospy.init_node("gripper_control")
    gripper = Gripper()
    rospy.loginfo("Gripper control node started")
    rospy.spin()