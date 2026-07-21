FROM ubuntu:20.04
# start with the nvidia container with Ubuntu 20.04

LABEL maintainer="Lukas Rustler <lukas.rustler@fel.cvut.cz>"

#Non-interactive mode
ENV DEBIAN_FRONTEND='noninteractive'

#Change for other python; 3.11 may be too much right now
ARG PYTHON_VER=3.8

#Install all neccesary thingies
RUN apt update -y && apt install software-properties-common -y && add-apt-repository ppa:deadsnakes/ppa -y  \
    && apt update && apt install python$PYTHON_VER wget sudo gedit unzip apt-utils curl \
    python$PYTHON_VER-venv nano mesa-utils curl htop net-tools sshfs python$PYTHON_VER-distutils  \
    screen git python$PYTHON_VER-dev libpng-dev libqhull-dev libfreetype6-dev libfreetype6  \
    pkg-config python3.8-venv python3.8-dev xvfb xdotool imagemagick  -y
    
#Install all pip dependencies as system packages
RUN apt install python3-testresources -y

#Install pips
# 3.8 is default at Ubuntu 20.04 and is fine for thing that do not work on newer versions
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python$PYTHON_VER || curl -sS https://bootstrap.pypa.io/pip/$PYTHON_VER/get-pip.py | python$PYTHON_VER
RUN curl -sS https://bootstrap.pypa.io/pip/3.8/get-pip.py | python3.8 && python3.8 -m pip install --upgrade pip

#Default args, that can be changed during build
ARG UID=1000
ARG GID=1000

# SSH
RUN apt install openssh-server -y && sed -i 's/\(^Port\)/#\1/' /etc/ssh/sshd_config &&  \
    echo Port 2222 >> /etc/ssh/sshd_config && service ssh start

# PyCharm
ARG PYCHARM_VER='2025.2.0.1'
RUN cd /opt && wget https://download.jetbrains.com/python/pycharm-community-$PYCHARM_VER.tar.gz &&  \
    tar -xvf pycharm-community-$PYCHARM_VER.tar.gz && rm pycharm-community-$PYCHARM_VER.tar.gz &&  \
    mv pycharm-community-$PYCHARM_VER pycharm && ln -s /opt/pycharm/bin/pycharm.sh /usr/bin/pycharm && chmod +x /usr/bin/pycharm

#ROS
RUN sh -c 'echo "deb http://packages.ros.org/ros/ubuntu focal main" > /etc/apt/sources.list.d/ros-latest.list' && \
    curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | apt-key add - && \
    apt update && apt install ros-noetic-desktop-full python3-rosdep python3-rosinstall python3-rosinstall-generator \
    python3-wstool build-essential python3-rosdep python3-catkin-tools ros-noetic-moveit* \
    ros-noetic-ddynamic-reconfigure* libglfw3-dev ros-noetic-effort* ros-noetic-ros-control* ros-noetic-rgbd-launch -y

# Calculation libraries
RUN python3.8 -m pip install importlib_metadata --force-reinstall
RUN python3.8 -m pip install numpy==1.24.4 scipy colour pybullet open3d --ignore-installed --no-cache-dir
    
#Add docker user with correct UID and GID; and add him to sudoers
RUN groupadd -g $GID docker_users && useradd -l -u $UID -G $GID -md /home/docker -s /bin/bash docker && \
    echo 'docker:docker' | chpasswd && usermod -aG sudo docker && \
    sed -i.bkp -e 's/%sudo\s\+ALL=(ALL\(:ALL\)\?)\s\+ALL/%sudo ALL=NOPASSWD:ALL/g' /etc/sudoers && \
    echo "docker  ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER docker
WORKDIR /home/docker
    
# UR
RUN sudo apt install ros-noetic-trac-ik-kinematics-plugin ros-noetic-rqt-joint-trajectory-controller  \
    ros-noetic-industrial-robot-status-interface ros-noetic-scaled-joint-trajectory-controller  \
    ros-noetic-speed-scaling-state-controller ros-noetic-ur-msgs ros-noetic-pass-through-controllers  \
    ros-noetic-ur-client-library -y && sudo rosdep init && sudo rosdep update && python3 -m pip install modbus-tk

# Make sure that catkin packages build on start
RUN echo "#!/bin/env bash\n\
echo 'Initializing the workspace';\n\
cd pyur/ || cd data/;\n\
catkin config --init --extend /opt/ros/noetic;\n\
catkin build;\n\
clear\n\n" >> /home/docker/build && chmod +x /home/docker/build

RUN python3 -m pip install pickle5 "numpy<2"
# Export variables
RUN echo "export PATH=$PATH:/home/docker/.local/bin" >> /home/docker/.bashrc && echo "source /home/docker/data/devel/setup.bash" >> /home/docker/.bashrc
RUN echo "export DISABLE_ROS1_EOL_WARNINGS=true" >> /home/docker/.bashrc

# Delete thingies from aptitude
RUN sudo rm -Rf /var/lib/apt/lists/*

WORKDIR /home/docker
ENTRYPOINT sudo service ssh start >> /dev/null && /bin/bash
