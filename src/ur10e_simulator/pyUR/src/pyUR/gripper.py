import os
import numpy as np


class RG6:
    JOINTS = ["left_inner_knuckle_joint", "left_inner_finger_joint", "right_outer_knuckle_joint",
              "right_inner_knuckle_joint", "right_inner_finger_joint"]
    SIGNS = [-1, 1, -1, -1, 1]

    def __init__(self, client):
        """
        Class for the RG6

        :param client: instance of Client, holding info about the scene
        :type client: Client
        """
        self.client = client
        self.id = client.robot
        self.control_joint_name = "finger_joint"
        self.max_force = 180
        self.constraints, self.finger_joint_id, self.finger_info = self.prepare_gripper()
        self.name = "gripper"
        self.finger_links_ids = [_.robot_link_id for _ in self.client.links if "finger" in _.name]
        self.all_finger_links_ids = [_.robot_link_id for _ in self.client.links if "finger" in _.name or "knuckle" in _.name]



        self.joint_ref = self.client.joints[self.client.find_joint_id(self.control_joint_name)[1]]

    def prepare_gripper(self):
        """
        Sets constraints for joints to works as mimic joint in URDF

        :return:
        :rtype:
        """

        # find ids of the 6 articulated joints
        joints_ids = []
        finger_joint_id = -1
        for idx in range(self.client.getNumJoints(self.id)):
            j_name = self.client.getJointInfo(self.id, idx)[1].decode("UTF-8")
            if self.control_joint_name == j_name:
                finger_joint_id = idx
            if j_name in self.JOINTS:
                joints_ids.append((j_name, idx))

        assert finger_joint_id != -1, "Finger joint not found in the URDF"
        finger_info = self.client.getJointInfo(self.id, finger_joint_id)

        # Set constraints -> only one joint (finger_joint) is articulated in reality and 5 others should follow it
        # Set a gear constraint
        constraints = []
        for joint in joints_ids:
            idx = joint[1]
            s = self.SIGNS[self.JOINTS.index(joint[0])]
            constraints.append(self.client.createConstraint(self.id, finger_joint_id,
                                                            self.id, idx,
                                                            jointType=self.client.JOINT_GEAR,
                                                            jointAxis=[1, 0, 0],
                                                            parentFramePosition=[0, 0, 0],
                                                            childFramePosition=[0, 0, 0]))

            # Some have different direction, because of axes settings etc.
            self.client.changeConstraint(constraints[-1], gearRatio=-s,  # +1 in gear ratio means reverse direction
                                         maxForce=self.max_force, erp=1)
            self.client.setJointMotorControl2(self.id, idx, self.client.POSITION_CONTROL, targetVelocity=0, force=0)
        # self.client.setJointMotorControl2(self.id, finger_joint_id, self.client.POSITION_CONTROL, targetVelocity=0, force=0)

        return constraints, finger_joint_id, finger_info

    def reset_constraints(self):
        """
        Remove all constraints

        :return:
        :rtype:
        """
        for c in self.constraints:
            self.client.removeConstraint(c)

    def stop(self):
        position = self.client.getJointState(self.id, self.finger_joint_id)[0]
        self.client.setJointMotorControl2(self.id, self.finger_joint_id,
                                          controlMode=self.client.POSITION_CONTROL, targetPosition=position,
                                          force=self.finger_info[self.client.jointInfo["MAXFORCE"]],
                                          maxVelocity=self.finger_info[self.client.jointInfo["MAXVELOCITY"]])

    def set_gripper_pose(self, position, velocity=None, wait=False):
        """
        Set goal position of gripper

        :param position: position of the gripper
        :type position: float
        :param wait: whether to wait for the motion to finish
        :type wait: bool
        :return:
        :rtype:
        """
        assert 0 <= position <= 150, "Gripper width must be between 0 and 150"
        joints_min = 0.6
        joint_max = -0.6
        position = ((position - 0) / (150 - 0)) * (joint_max - joints_min) + joints_min
        self.client.move_position(self.control_joint_name, position, velocity=velocity, wait=wait)


class Softhand:
    JOINTS = ['qbhand_thumb_knuckle_joint', 'qbhand_thumb_proximal_joint', 'qbhand_thumb_proximal_virtual_joint', 'qbhand_thumb_distal_joint', 'qbhand_thumb_distal_virtual_joint', 'qbhand_index_knuckle_joint', 'qbhand_index_proximal_joint', 'qbhand_index_proximal_virtual_joint', 'qbhand_index_middle_joint', 'qbhand_index_middle_virtual_joint', 'qbhand_index_distal_joint', 'qbhand_index_distal_virtual_joint', 'qbhand_middle_knuckle_joint', 'qbhand_middle_proximal_joint', 'qbhand_middle_proximal_virtual_joint', 'qbhand_middle_middle_joint', 'qbhand_middle_middle_virtual_joint', 'qbhand_middle_distal_joint', 'qbhand_middle_distal_virtual_joint', 'qbhand_ring_knuckle_joint', 'qbhand_ring_proximal_joint', 'qbhand_ring_proximal_virtual_joint', 'qbhand_ring_middle_joint', 'qbhand_ring_middle_virtual_joint', 'qbhand_ring_distal_joint', 'qbhand_ring_distal_virtual_joint', 'qbhand_little_knuckle_joint', 'qbhand_little_proximal_joint', 'qbhand_little_proximal_virtual_joint', 'qbhand_little_middle_joint', 'qbhand_little_middle_virtual_joint', 'qbhand_little_distal_joint', 'qbhand_little_distal_virtual_joint']
    MIMIC_JOINTS = ['qbhand_synergy_joint', 'qbhand_synergy_joint', 'qbhand_thumb_proximal_joint', 'qbhand_synergy_joint', 'qbhand_thumb_distal_joint', 'qbhand_synergy_joint', 'qbhand_synergy_joint', 'qbhand_index_proximal_joint', 'qbhand_synergy_joint', 'qbhand_index_middle_joint', 'qbhand_synergy_joint', 'qbhand_index_distal_joint', 'qbhand_synergy_joint', 'qbhand_synergy_joint', 'qbhand_middle_proximal_joint', 'qbhand_synergy_joint', 'qbhand_middle_middle_joint', 'qbhand_synergy_joint', 'qbhand_middle_distal_joint', 'qbhand_synergy_joint', 'qbhand_synergy_joint', 'qbhand_ring_proximal_joint', 'qbhand_synergy_joint', 'qbhand_ring_middle_joint', 'qbhand_synergy_joint', 'qbhand_ring_distal_joint', 'qbhand_synergy_joint', 'qbhand_synergy_joint', 'qbhand_little_proximal_joint', 'qbhand_synergy_joint', 'qbhand_little_middle_joint', 'qbhand_synergy_joint', 'qbhand_little_distal_joint']
    SIGNS = [2.542, 0.785, 1.0, 0.785, 1.0, -0.2, 0.785, 1.0, 0.785, 1.0, 0.785, 1.0, 0.0, 0.785, 1.0, 0.785, 1.0, 0.785, 1.0, 0.2, 0.785, 1.0, 0.785, 1.0, 0.785, 1.0, 0.4, 0.785, 1.0, 0.785, 1.0, 0.785, 1.0]

    def __init__(self, client):
        """
        Class for the RG6

        :param client: instance of Client, holding info about the scene
        :type client: Client
        """
        self.client = client
        self.id = client.robot
        self.control_joint_name = "qbhand_synergy_joint"
        self.finger_joint_id, self.finger_info, self.joints_ids = self.prepare_gripper()


        self.name = "gripper"
        self.finger_links_ids = [] #[_.robot_link_id for _ in self.client.links if "finger" in _.name]
        self.all_finger_links_ids = [_.robot_link_id for _ in self.client.links if "qbhand" in _.name]



        self.joint_ref = self.client.joints[self.client.find_joint_id(self.control_joint_name)[1]]

    def prepare_gripper(self):
        """
        Sets constraints for joints to works as mimic joint in URDF

        :return:
        :rtype:
        """

        # find ids of the articulated joints
        joints_ids = []
        finger_joint_id = -1
        for j_name_ in self.JOINTS:
            for idx in range(self.client.getNumJoints(self.id)):
                j_name = self.client.getJointInfo(self.id, idx)[1].decode("UTF-8")
                if finger_joint_id == -1 and self.control_joint_name == j_name:
                    finger_joint_id = idx
                if j_name == j_name_:
                    joints_ids.append(idx)

        assert finger_joint_id != -1, "Finger joint not found in the URDF"
        finger_info = self.client.getJointInfo(self.id, finger_joint_id)

        for joint_order_id, joint in enumerate(joints_ids):
            idx = joint
            self.client.setJointMotorControl2(
                bodyIndex=self.id,
                jointIndex=idx,
                controlMode=self.client.POSITION_CONTROL,
                targetPosition=0.0,
                force=1
            )
            self.client.resetJointState(self.id, idx, 0)

        self.client.setJointMotorControl2(self.id, finger_joint_id, self.client.POSITION_CONTROL, targetVelocity=0, force=1)
        self.client.resetJointState(self.id, finger_joint_id, 0)

        return finger_joint_id, finger_info, joints_ids

    def stop(self):
        position = self.client.getJointState(self.id, self.finger_joint_id)[0]
        self.client.setJointMotorControl2(self.id, self.finger_joint_id,
                                          controlMode=self.client.POSITION_CONTROL, targetPosition=position,
                                          force=self.finger_info[self.client.jointInfo["MAXFORCE"]],
                                          maxVelocity=self.finger_info[self.client.jointInfo["MAXVELOCITY"]])

    def set_gripper_pose(self, position, velocity=0.5, wait=False):
        """
        Set goal position of gripper

        :param position: position of the gripper
        :type position: float
        :param wait: whether to wait for the motion to finish
        :type wait: bool
        :return:
        :rtype:
        """
        assert 0 <= position <= 1, "Gripper width must be between 0 and 1"
        self.client.logger.info("Setting gripper pose to: {}".format(position))
        self.client.move_position(self.control_joint_name, 1-position, velocity=velocity, wait=wait)