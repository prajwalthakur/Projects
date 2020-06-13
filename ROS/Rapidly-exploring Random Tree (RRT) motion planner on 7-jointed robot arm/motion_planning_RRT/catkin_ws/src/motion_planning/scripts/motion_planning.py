#!/usr/bin/env python

"""
This is a skeleton code.
"""

from copy import deepcopy
import math
import numpy
import random
from threading import Thread, Lock
import sys

import actionlib
import control_msgs.msg
import geometry_msgs.msg
import moveit_commander
import moveit_msgs.msg
import moveit_msgs.srv
import rospy
import sensor_msgs.msg
import tf
import trajectory_msgs.msg

def convert_to_message(T):
    t = geometry_msgs.msg.Pose()
    position = tf.transformations.translation_from_matrix(T)
    orientation = tf.transformations.quaternion_from_matrix(T)
    t.position.x = position[0]
    t.position.y = position[1]
    t.position.z = position[2]
    t.orientation.x = orientation[0]
    t.orientation.y = orientation[1]
    t.orientation.z = orientation[2]
    t.orientation.w = orientation[3]        
    return t

def convert_from_message(msg):
    R = tf.transformations.quaternion_matrix((msg.orientation.x,
                                              msg.orientation.y,
                                              msg.orientation.z,
                                              msg.orientation.w))
    T = tf.transformations.translation_matrix((msg.position.x, 
                                               msg.position.y, 
                                               msg.position.z))
    return numpy.dot(T,R)

def convert_from_trans_message(msg):
    R = tf.transformations.quaternion_matrix((msg.rotation.x,
                                              msg.rotation.y,
                                              msg.rotation.z,
                                              msg.rotation.w))
    T = tf.transformations.translation_matrix((msg.translation.x, 
                                               msg.translation.y, 
                                               msg.translation.z))
    return numpy.dot(T,R)
   
class ListNode:
    def __init__(self, data,distance_parent="inf"):
        "constructor to initiate this object"
        
        # store data
        self.data = data
        self.distance_parent=distance_parent
        # store reference (next item)
        self.parent = None
        return    
            


class MoveArm(object):

    def __init__(self):
        print "Motion Planning Initializing..."
        # Prepare the mutex for synchronization
        self.mutex = Lock()

        # Some info and conventions about the robot that we hard-code in here
        # min and max joint values are not read in Python urdf, so we must hard-code them here
        self.num_joints = 7
        self.q_min = []
        self.q_max = []
        self.q_min.append(-3.1459);self.q_max.append(3.1459)
        self.q_min.append(-3.1459);self.q_max.append(3.1459)
        self.q_min.append(-3.1459);self.q_max.append(3.1459)
        self.q_min.append(-3.1459);self.q_max.append(3.1459)
        self.q_min.append(-3.1459);self.q_max.append(3.1459)
        self.q_min.append(-3.1459);self.q_max.append(3.1459)
        self.q_min.append(-3.1459);self.q_max.append(3.1459)
        # How finely to sample each joint
        self.q_sample = [0.05, 0.05, 0.05, 0.1, 0.1, 0.1, 0.1]
        self.joint_names = ["lwr_arm_0_joint",
                            "lwr_arm_1_joint",
                            "lwr_arm_2_joint",
                            "lwr_arm_3_joint",
                            "lwr_arm_4_joint",
                            "lwr_arm_5_joint",
                            "lwr_arm_6_joint"]

        # Subscribes to information about what the current joint values are.
        rospy.Subscriber("/joint_states", sensor_msgs.msg.JointState, 
                         self.joint_states_callback)

        # Subscribe to command for motion planning goal
        rospy.Subscriber("/motion_planning_goal", geometry_msgs.msg.Transform,
                         self.move_arm_cb)

        # Publish trajectory command
        self.pub_trajectory = rospy.Publisher("/joint_trajectory", trajectory_msgs.msg.JointTrajectory, 
                                              queue_size=1)        

        # Initialize variables
        self.joint_state = sensor_msgs.msg.JointState()

        # Wait for moveit IK service
        rospy.wait_for_service("compute_ik")
        self.ik_service = rospy.ServiceProxy('compute_ik',  moveit_msgs.srv.GetPositionIK)
        print "IK service ready"

        # Wait for validity check service
        rospy.wait_for_service("check_state_validity")
        self.state_valid_service = rospy.ServiceProxy('check_state_validity',  
                                                      moveit_msgs.srv.GetStateValidity)
        print "State validity service ready"

        # Initialize MoveIt
        self.robot = moveit_commander.RobotCommander()
        self.scene = moveit_commander.PlanningSceneInterface()
        self.group_name = "lwr_arm"
        self.group = moveit_commander.MoveGroupCommander(self.group_name) 
        print "MoveIt! interface ready"

        # Options
        self.subsample_trajectory = True
        print "Initialization done."

    def get_joint_val(self, joint_state, name):
        if name not in joint_state.name:
            print "ERROR: joint name not found"
            return 0
        i = joint_state.name.index(name)
        return joint_state.position[i]

    def set_joint_val(self, joint_state, q, name):
        if name not in joint_state.name:
            print "ERROR: joint name not found"
        i = joint_state.name.index(name)
        joint_state.position[i] = q

    """ Given a complete joint_state data structure, this function finds the values for 
    our arm's set of joints in a particular order and returns a list q[] containing just 
    those values.
    """
    def q_from_joint_state(self, joint_state):
        q = []
        for i in range(0,self.num_joints):
            q.append(self.get_joint_val(joint_state, self.joint_names[i]))
        return q

    """ Given a list q[] of joint values and an already populated joint_state, this 
    function assumes that the passed in values are for a our arm's set of joints in 
    a particular order and edits the joint_state data structure to set the values 
    to the ones passed in.
    """
    def joint_state_from_q(self, joint_state, q):
        for i in range(0,self.num_joints):
            self.set_joint_val(joint_state, q[i], self.joint_names[i])

    """ This function will perform IK for a given transform T of the end-effector. It 
    returns a list q[] of 7 values, which are the result positions for the 7 joints of 
    the left arm, ordered from proximal to distal. If no IK solution is found, it 
    returns an empy list.
    """
    def IK(self, T_goal):
        req = moveit_msgs.srv.GetPositionIKRequest()
        req.ik_request.group_name = self.group_name
        req.ik_request.robot_state = moveit_msgs.msg.RobotState()
        req.ik_request.robot_state.joint_state = self.joint_state
        req.ik_request.avoid_collisions = True
        req.ik_request.pose_stamped = geometry_msgs.msg.PoseStamped()
        req.ik_request.pose_stamped.header.frame_id = "world_link"
        req.ik_request.pose_stamped.header.stamp = rospy.get_rostime()
        req.ik_request.pose_stamped.pose = convert_to_message(T_goal)
        req.ik_request.timeout = rospy.Duration(3.0)
        res = self.ik_service(req)
        q = []
        if res.error_code.val == res.error_code.SUCCESS:
            q = self.q_from_joint_state(res.solution.joint_state)
        return q

    """ This function checks if a set of joint angles q[] creates a valid state, or 
    one that is free of collisions. The values in q[] are assumed to be values for 
    the joints of the left arm, ordered from proximal to distal. 
    """
    def is_state_valid(self, q):
        req = moveit_msgs.srv.GetStateValidityRequest()
        req.group_name = self.group_name
        current_joint_state = deepcopy(self.joint_state)
        current_joint_state.position = list(current_joint_state.position)
        self.joint_state_from_q(current_joint_state, q)
        req.robot_state = moveit_msgs.msg.RobotState()
        req.robot_state.joint_state = current_joint_state
        res = self.state_valid_service(req)
        return res.valid
    
    def random_points_create(self,q_min,q_max):
        random_points=numpy.random.uniform(q_min[0],q_max[0],7)
        return random_points
    
    def unit_vect(self,l,m):
        l=numpy.array(l)
        m=numpy.array(m)
        parent_t_child_vector=numpy.array(l-m)/numpy.linalg.norm((l-m))
        return parent_t_child_vector
    
    def calculate_distance(self,qv_list,random_joint_point):
        q_array=numpy.array(qv_list)
        random_joint_point=numpy.array(random_joint_point)
        #print(q_array)
        distance2=q_array-random_joint_point
        if len(q_array.shape)==2:
            distance=numpy.linalg.norm(distance2,axis=1)
            index=numpy.argmin(distance)
            min_dist=distance[index]
        else:
            distance=numpy.linalg.norm(distance2)
            index=0
            min_dist=distance
        

        return index,min_dist
    
    def closet_point_toward_node(self,vector_ba,a_vec,b_vec,discrete_range):
        
        b_vec=numpy.array(b_vec)
        a_vec=numpy.array(a_vec)
        vector_ba=numpy.array(vector_ba)
        #vector_points=numpy.zeros((7,3))
        r1=numpy.linalg.norm((b_vec-a_vec))
        closet_point=numpy.zeros((7,))
        #print("vector_ba",vector_ba,"b_vec",b_vec,"a_vec",a_vec,"disc_range",discrete_range,"closet_point",closet_point)
        #if(r1<0.2):
            #closet_point=a_vec
            #print("b_vec",b_vec)
           #print("closet_point",closet_point)
            #return closet_point
        #else:
        r2=r1/discrete_range
        r3=math.ceil(r2)
        r4=int(r3)
        #r4=r4+2
        #print("vector_ba",vector_ba)
        vector_points=numpy.array([b_vec+vector_ba*discrete_range*i for i  in range(0,r4)])
        #i=0
        #closet_point=numpy.zeros((1,7))
        #print("vector_points=",vector_points)
        #print("r1",r1,"vectors=",vector_points.shape)
        #print("before",vector_points[0])
        (row,col)=vector_points.shape
        
        vector_points_index=numpy.argsort(numpy.linalg.norm((vector_points-b_vec),axis=1))
        #vector_points_index=numpy.flip(vector_points_index)
        vector_points=vector_points[vector_points_index]
        # print("after",vector_points[0])
        #print("row=",numpy.linalg.norm((vector_points-b_vec),axis=1))
        i=0
        while(i<row ): 
            if (self.is_state_valid(vector_points[i])==True):
                #print("i=",numpy.linalg.norm((vector_points[i]-b_vec)))
                
                closet_point=vector_points[i]
                # print("row",row,"i",i,"vector_points[i]",vector_points[i])
                i=i+1
                #temp=closet_point
            else:
                break
          
        
            #print("closet_point",closet_point)
        return closet_point
                    
            


    def is_collision_free_path(self,a,b,discrete_range):
        vectorba=self.unit_vect(a,b)
       #print("vectorba=",vectorba)
        closet_point_toward_a_without_collision=self.closet_point_toward_node(vectorba,a,b,discrete_range)
        index,distance=self.calculate_distance(a,closet_point_toward_a_without_collision)
        #numpy.linalg.norm((numpy.array(a)-closet_point_toward_a_without_collision))
        if distance<discrete_range:
            status=True
        else:
            status=False
        return closet_point_toward_a_without_collision,status

    def motion_plan(self, q_start, q_goal, q_min, q_max):
        print("after entering the motion_planning")

        maximum_time_secs = 15
        begin = rospy.get_rostime().secs
        now = rospy.get_rostime().secs
        # Replace this with your own planner code
        #joint_states=[]
        q_list = []
        d={}
        d["points"+str(0)]=ListNode(numpy.array(q_start))
        goal=ListNode(q_goal)
        qv_list=[]
        qv_list.append(numpy.array(d["points"+str(0)].data))
        
        #sampling one joint_point
        p=1
        flag=0 #indicating goal reached
        random_range=0.2
       # print("d[points+str(0)]=",d["points"+str(0)].data)
        while(flag!=1 and (now-begin)<10):
            random_joint_point=self.random_points_create(q_min,q_max)
            if (self.is_state_valid(random_joint_point)):
                
                #calculating minimum distance of this node to the nodes of the tree
                index,min_distance=self.calculate_distance(qv_list,random_joint_point)
                #d["points"+str(p)].data=min_distance
                closet_point_,status=self.is_collision_free_path(random_joint_point,qv_list[index],random_range)
                if status:
                    d["points"+str(p)]=ListNode(random_joint_point)
                    d["points"+str(p)].parent=d["points"+str(index)]
                    qv_list.append(d["points"+str(p)].data)
                else:
                    d["points"+str(p)]=ListNode(closet_point_)
                    d["points"+str(p)].parent=d["points"+str(index)]
                    qv_list.append(d["points"+str(p)].data)

                closet_point_,status=self.is_collision_free_path(goal.data,d["points"+str(p)].data,random_range)
                if status:
                    goal.parent=d["points"+str(p)]
                    print("meet")
                    flag=1
                else:
                    p=p+1
                    d["points"+str(p)]=ListNode(closet_point_)
                    d["points"+str(p)].parent=d["points"+str(p-1)]
                    qv_list.append(d["points"+str(p)].data)

                    

                p=p+1
            now = rospy.get_rostime().secs
        now=rospy.get_rostime().secs
        if(flag==1):
            p=1
            print("path found")
            parent_node=goal.parent
            q_list.append(goal.data)
            #print(d)
            #print(q_list)
            while parent_node!=None:
                poi=parent_node.data.tolist()
                q_list.append(poi)
                parent_node=parent_node.parent
                #print(q_list)
            q_list.reverse() 
                #print("q",q_list)
            q_list_copy = []
                
            #q_list_copy.append(q_list[0])
            #for i in range(len(q_list)-2):
            #    if self.is_collision_free_path(q_list[i], q_list[i+2]) == False:
            #        q_list_copy.append(q_list[i])
           # q_list_copy.append(q_list[-1])
            #q_list = q_list_copy                
        
        else:
            print("p",p,"now-begin",now-begin)
            print("path not found")      
        #print("q",q_list)        
        print("p",p,"now-begin",now-begin)
        print(q_list)
        return q_list
    # ===========================

    
    def create_trajectory(self, q_list, v_list, a_list, t):
        joint_trajectory = trajectory_msgs.msg.JointTrajectory()
        for i in range(0, len(q_list)):
            point = trajectory_msgs.msg.JointTrajectoryPoint()
            point.positions = list(q_list[i])
            point.velocities = list(v_list[i])
            point.accelerations = list(a_list[i])
            point.time_from_start = rospy.Duration(t[i])
            joint_trajectory.points.append(point)
        joint_trajectory.joint_names = self.joint_names
        return joint_trajectory

    def create_trajectory(self, q_list):
        joint_trajectory = trajectory_msgs.msg.JointTrajectory()
        for i in range(0, len(q_list)):
            point = trajectory_msgs.msg.JointTrajectoryPoint()
            point.positions = list(q_list[i])
            joint_trajectory.points.append(point)
        joint_trajectory.joint_names = self.joint_names
        return joint_trajectory

    def project_plan(self, q_start, q_goal, q_min, q_max):
        print("before entering the motion_planning")
        q_list=[]
        q_list=self.motion_plan(q_start, q_goal, q_min, q_max)
        #print(q_list) 
        joint_trajectory = self.create_trajectory(q_list)
        return joint_trajectory

    def move_arm_cb(self, msg):
        T = convert_from_trans_message(msg)
        self.mutex.acquire()
        q_start = self.q_from_joint_state(self.joint_state)
        print "Solving IK"
        q_goal = self.IK(T)
        if len(q_goal)==0:
            print "IK failed, aborting"
            self.mutex.release()
            return
        print "IK solved, planning"
        trajectory = self.project_plan(numpy.array(q_start), q_goal, self.q_min, self.q_max)
        if not trajectory.points:
            print "Motion plan failed, aborting"
        else:
            print "Trajectory received with " + str(len(trajectory.points)) + " points"
            self.execute(trajectory)
        self.mutex.release()
        
    def joint_states_callback(self, joint_state):
        self.mutex.acquire()
        self.joint_state = joint_state
        self.mutex.release()

    def execute(self, joint_trajectory):
        self.pub_trajectory.publish(joint_trajectory)

if __name__ == '__main__':
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('move_arm', anonymous=True)
    ma = MoveArm()
    rospy.spin()
