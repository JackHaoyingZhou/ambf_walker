#!/usr/bin/env python
import smach
import rospy
import numpy as np
from sensor_msgs.msg import JointState
from ambf_walker.msg import DesiredJoints
from StateMachines.States import Initialize, Stabilize, GMRTest

class ExoStateMachine(object):

    def __init__(self, model):
        sm = smach.StateMachine(outcomes=['outcome4'])

        with sm:
            smach.StateMachine.add('Initialize', Initialize(model=model),
                                    transitions={'Initializing': 'Initialize',
                                                  'Initialized': 'Stabilize'})

            smach.StateMachine.add('Stabilize', Stabilize(model),
                                   transitions={'Stabilizing': 'Stabilize',
                                                'Stabilized': 'outcome4'})

        outcome = sm.execute()



class ExoStateMachineTest(object):

    def __init__(self, model):
        sm = smach.StateMachine(outcomes=['outcome4'])

        with sm:
            smach.StateMachine.add('Initialize', Initialize(model=model),
                                    transitions={'Initializing': 'Initialize',
                                                  'Initialized': 'Follow'})

            smach.StateMachine.add('Follow', GMRTest(model),
                                   transitions={'Following': 'Follow',
                                                'Followed': 'Follow'})

        outcome = sm.execute()