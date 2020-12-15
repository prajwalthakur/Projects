**RRT MOTION PLANNER IN ROS MELODIC**

requirements:

ROS-MELODIC

![](.//media/image1.gif)

To simulate:

1.download the Repositary

2.Build the catkin directory by catkin\_make or catkin build

3.source /opt/ros/kinetic/setup.bash

4.source /devel/setup.bash

5.To run the project, first open up a terminal and run "roslaunch
motion\_planning mp.launch".In the second terminal,run"rosrun
motion\_planning marker\_control.py".

6.On another 2 separate terminals, run "rosrun motion\_planning
motion\_planning.py", and "rosrun rviz rviz" to visualize the robot.

7.On rviz, you will need to add a RobotModel, InteractiveMarker, and
Marker. When you add the InteractiveMarker, click on "InteractiveMarker"
to expand it, and select /control\_markers/update as the update topic.
