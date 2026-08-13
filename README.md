# UR10e python simulator with virtual AIRSKIN

This folder contains necessary files to run the simulation of the UR10e robot with virtual AIRSKIN.

## Contents

 - [Installation](#installation)
 - [Docker Installation](#docker-installation)
 - [Citation](#citation)
 - [Code](#code)
 - [Run](#run)

## Installation
  - clone this repository

        cd SOME_PATH
        git clone --recursive https://github.com/Humanoids-CTU/pyUR.git pyur_ws

  - use Docker (see [Docker Installation](#docker-installation)) or install ROS Noetic (+ required libraries from
    [Dockerfile](Docker/Dockerfile)) and Python 3.8 (with `pybullet`, `open3d`, and their dependencies)
  - if using Docker

        cd pyur_ws/Docker
        ./deploy.py -c pyur -p SOME_PATH/pyur_ws -b
    - the above will build the Docker image, rename the container to `pyur`, and run it. You can also:
      - `./deploy.py -c pyur -e` to run an already built container
      - `./deploy.py -c pyur -t` to open a new terminal in the container
      - see [easy-docker](https://github.com/rustlluk/easy-docker) for more `deploy.py` options
  - build the workspace (inside docker; otherwise cd to where your workspace is)

        cd data
        catkin config --extend /opt/ros/noetic --init
        catkin build
  - source the workspace

        source devel/setup.bash

## Docker Installation
  - **Works only on GNU/Linux systems**
  - install [docker-engine](https://docs.docker.com/engine/install/ubuntu/)
  - **do not install Docker Desktop**
    - Docker Desktop is not the same as docker-engine and does not work the same way here
  - do not forget [post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/)
  - (optional) install [nvidia-docker](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
    for GPU support

For more commands and FAQ see [easy-docker](https://github.com/rustlluk/easy-docker).

## Citation
If you use this simulator, cite the adaptive-skin paper:

```bibtex
@inproceedings{rustler2024adaptive,
  title={{Adaptive Electronic Skin Sensitivity for Safe Human-Robot Interaction}},
  author={Rustler, Lukas and Misar, Matej and Hoffmann, Matej},
  booktitle={2024 IEEE-RAS 23rd International Conference on Humanoid Robots (Humanoids)},
  pages={475--482},
  year={2024},
  organization={IEEE}
}
```

## Code
**A bit older version, but the core is the same**  
The documentation PDF can be found in [ur10ewithairskin.pdf](documentation/ur10ewithairskin.pdf).  
Online documentation is available at [lukasrustler.cz/pyur](https://lukasrustler.cz/pyur/).


## Run
The simulator can be run in two mode:
  1) ROS version - real-time, high-level planners (MoveIt!, ...)
  2) Native - much faster than real-time, only low-level control 
### ROS version
  - install necessary things and build the workspace
    - see [Installation](#Installation)
  - run the simulator
    - in the terminal, run

          roslaunch bullet_ros_ur simulation.launch
      - you can specify parameter  `gripper:=` with values:  
        - false - no gripper,
        - true - RG6 gripper (this for backwards compatibility with frameworks specifying only true/false)
        - rg6 - RG gripper
        - softhand - QB SoftHand gripper
    - this will start the simulator and RVIZ with the robot
#### Control the robot
 - to test the connection etc. you can just move the robot in RVIZ and plan
   from there
 - or, see [examples.py](src/ur10e_simulator/bullet_ros_ur/scripts/examples.py)
   - it shows how to control the robot, gripper. How to play trajectories and how
     to get IK without moving
 - the simulated robot provides `position_controllers/ScaledJointTrajectoryController` and 
   `velocity_controllers/JointGroupVelocityController`, i.e., waypoint controller through moveit or direct assignment
   of joint velocities to the joints
   - the default is `ScaledJointTrajectoryController`. You need to switch with rosservice `/controller_manager/switch_controller`
     before running joint commands
     - see [examples.py](src/ur10e_simulator/bullet_ros_ur/scripts/examples.py) for an example
 - the simulator also provides Cartesian controllers (motion, force, compliance) from the
   [cartesian_controllers](https://github.com/fzi-forschungszentrum-informatik/cartesian_controllers) package
   - see [examples.py](src/ur10e_simulator/bullet_ros_ur/scripts/examples.py) for examples of:
    - controlling the robot by publishing a target pose to `/robot/target_frame` (`CartesianMotionController`)
    - commanding a target wrench to `/robot/target_wrench` (`CartesianForceController`)
    - combining pose and wrench targets (`CartesianComplianceController`)
    - using the interactive RViz marker (`motion_control_handle`) for drag-and-drop Cartesian control

### Non-ROS version
  - install necessary things
    - see [Installation](#Installation)
  - you can run examples from [examples](src/ur10e_simulator/pyUR/examples) folder
    - scripts [cartesian_example.py](src/ur10e_simulator/pyUR/examples/cartesian_example.py) and
      [joints_example.py](src/ur10e_simulator/pyUR/examples/joints_example.py) show how to control the robot in 
      cartesian and joint space, respectively.