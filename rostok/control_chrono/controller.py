from typing import Any, Dict, List, Tuple
from math import sin

import pychrono.core as chrono

from rostok.block_builder_chrono.block_classes import (ChronoRevolveJoint, JointInputTypeChrono)
from rostok.virtual_experiment.sensors import Sensor

class RobotControllerChrono:

    def __init__(self, joint_vector, parameters: Dict[int, Any]):
        self.joints: List[Tuple[int, ChronoRevolveJoint]] = joint_vector
        self.initialize_functions(parameters)
        self.parameters = parameters

    def initialize_functions(self, parameters):
        if len(parameters) != len(self.joints):
            raise Exception("some joints are not parametrized")

        for i, joint in enumerate(self.joints):
            chr_function = chrono.ChFunction_Const(float(parameters[i]))
            joint[1].joint.SetTorqueFunction(chr_function)

    def update_functions(self, time, parameters, robot_data, environment_data):
        pass

class SinControllerChronoFn(RobotControllerChrono):

    def __init__(self, joint_vector, parameters: Dict[int, Any]):
        super().__init__(joint_vector, parameters)

    def initialize_functions(self, parameters):
        if len(parameters) != len(self.joints):
            raise Exception("some joints are not parametrized")
        for i, joint in enumerate(self.joints):
            #joint[1].joint.SetTorqueFunction(chrono.ChFunction_Const(0.0))
            chr_function = chrono.ChFunction_Sine(0.0, parameters[i][1]/6.28, parameters[i][0])
            joint[1].joint.SetTorqueFunction(chr_function)

    def update_functions(self, time, parameters, robot_data, environment_data):
        # for i, joint in enumerate(self.joints):
        #     current_const = parameters[i][0]*sin(parameters[i][1]*time)
        #     chr_function = chrono.ChFunction_Const(current_const)
            
        #     joint[1].joint.SetTorqueFunction(chr_function)
        pass

class SinControllerChrono(RobotControllerChrono):

    def __init__(self, joint_vector, parameters: Dict[int, Any]):
        super().__init__(joint_vector, parameters)

    def initialize_functions(self, parameters):
        if len(parameters) != len(self.joints):
            raise Exception("some joints are not parametrized")
        for i, joint in enumerate(self.joints):
            joint[1].joint.SetTorqueFunction(chrono.ChFunction_Const(0.0))

    def update_functions(self, time, parameters, robot_data, environment_data):
        for i, joint in enumerate(self.joints):
            current_const = parameters[i][0]*sin(parameters[i][1]*time)
            chr_function = chrono.ChFunction_Const(current_const)
            
            joint[1].joint.SetTorqueFunction(chr_function)

class ConstReverseControllerChrono(RobotControllerChrono):

    def __init__(self, joint_vector, parameters: Dict[int, Any]):
        super().__init__(joint_vector, parameters)

    def initialize_functions(self, parameters):
        if len(parameters) != len(self.joints):
            raise Exception("some joints are not parametrized")
        for i, joint in enumerate(self.joints):
            joint[1].joint.SetTorqueFunction(chrono.ChFunction_Const(0.0))

    def update_functions(self, time, parameters, robot_data:Sensor, environment_data):
        robot_data.
