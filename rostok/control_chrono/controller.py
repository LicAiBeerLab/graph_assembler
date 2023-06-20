from math import sin
from typing import Any, Dict, List, Tuple
from abc import abstractmethod
from dataclasses import dataclass, field
from matplotlib.pyplot import cla

import pychrono.core as chrono
from typing import Callable, List
from rostok.block_builder_chrono.block_classes import (ChronoRevolveJoint, JointInputTypeChrono)

from rostok.virtual_experiment.sensors import Sensor


class RobotControllerChrono:
    """General controller. Any controller should be subclass of this class.
    
        Attributes:
            joints (List[Tuple[int, ChronoRevolveJoint]]): list of all joints in the mechanism
            parameters: vector of parameters for joints
            trajectories: trajectories for the joints
            functions: list of functions currently attached to joints
    """

    def __init__(self, joint_map_ordered, parameters: Dict[str, Any]):
        """Initialize class fields and call the initialize_functions() to set starting state"""
        self.joint_map_ordered: Dict[int, ChronoRevolveJoint] = joint_map_ordered
        self.parameters = parameters
        self.functions: List[chrono.ChFunction_Const] = []
        self.chrono_joint_setters: Dict[JointInputTypeChrono, str] = {}
        self.do_nothing = lambda x: None
        self.set_function()
        self.initialize_functions()

    def set_function(self):
        self.chrono_joint_setters = {
            JointInputTypeChrono.TORQUE: 'SetTorqueFunction',
            JointInputTypeChrono.VELOCITY: 'SetSpeedFunction',
            JointInputTypeChrono.POSITION: 'SetAngleFunction',
            JointInputTypeChrono.UNCONTROL: 'Uncontrol'
        }

    def initialize_functions(self):
        """Attach initial functions to the joints."""
        i = 0
        for idx, joint in self.joint_map_ordered.items():
            if self.chrono_joint_setters[joint.input_type] == 'Uncontrol':
                pass
            else:
                chr_function = chrono.ChFunction_Const(float(self.parameters["initial_value"][i]))
                joint_setter = getattr(joint.joint, self.chrono_joint_setters[joint.input_type])
                joint_setter(chr_function)
                self.functions.append(chr_function)
                i += 1

    @abstractmethod
    def update_functions(self, time, robot_data, environment_data):
        pass


class ConstController(RobotControllerChrono):

    def update_functions(self, time, robot_data, environment_data):
        pass


class SinControllerChrono(RobotControllerChrono):
    """Controller that sets sinusoidal torques using constant update at each step."""

    def update_functions(self, time, robot_data, environment_data):
        for i, func in enumerate(self.functions):
            current_const = self.parameters['sin_parameters'][i][0] * sin(
                self.parameters['sin_parameters'][i][1] * time)
            func.Set_yconst(current_const)


class LinearSinControllerChrono(RobotControllerChrono):
    """Controller that sets sinusoidal torques using constant update at each step."""

    def update_functions(self, time, robot_data, environment_data):
        for i, func in enumerate(self.functions):
            current_const = self.parameters['sin_parameters'][i][2] * time * self.parameters[
                'sin_parameters'][i][0] * sin(self.parameters['sin_parameters'][i][1] * time)
            func.Set_yconst(current_const)


@dataclass
class ForceTorque:
    """Forces and torques are given in the xyz convention
    """
    force: tuple[float, float, float] = (0, 0, 0)
    torque: tuple[float, float, float] = (0, 0, 0)


class ForceControllerTemplate():
    """Base class for creating force and moment actions. 
    To use it, you need to implement the get_force_torque method, 
    which determines the force and torque at time t. Vectors are 
    specified in global coordinate system.
    """

    def __init__(self) -> None:

        self.x_force_chrono = chrono.ChFunction_Const(0)
        self.y_force_chrono = chrono.ChFunction_Const(0)
        self.z_force_chrono = chrono.ChFunction_Const(0)

        self.x_torque_chrono = chrono.ChFunction_Const(0)
        self.y_torque_chrono = chrono.ChFunction_Const(0)
        self.z_torque_chrono = chrono.ChFunction_Const(0)

        self.force_vector_chrono = [self.x_force_chrono, self.y_force_chrono, self.z_force_chrono]
        self.torque_vector_chrono = [
            self.x_torque_chrono, self.y_torque_chrono, self.z_torque_chrono
        ]
        self.force_maker_chrono = chrono.ChForce()
        self.torque_maker_chrono = chrono.ChForce()
        self.is_binded = False
        self.setup_makers()

    @abstractmethod
    def get_force_torque(self, time: float, data) -> ForceTorque:
        pass

    def update(self, time: float, data=None):
        force_torque = self.get_force_torque(time, data)
        for val, functor in zip(force_torque.force + force_torque.torque,
                                self.force_vector_chrono + self.torque_vector_chrono):
            functor.Set_yconst(val)

    def setup_makers(self):
        self.force_maker_chrono.SetMode(chrono.ChForce.FORCE)
        self.force_maker_chrono.SetAlign(chrono.ChForce.WORLD_DIR)
        self.torque_maker_chrono.SetMode(chrono.ChForce.TORQUE)
        self.torque_maker_chrono.SetAlign(chrono.ChForce.WORLD_DIR)
        
        self.force_maker_chrono.SetF_x(self.x_force_chrono)
        self.force_maker_chrono.SetF_y(self.y_force_chrono)
        self.force_maker_chrono.SetF_z(self.z_force_chrono)

        self.torque_maker_chrono.SetF_x(self.x_torque_chrono)
        self.torque_maker_chrono.SetF_y(self.y_torque_chrono)
        self.torque_maker_chrono.SetF_z(self.z_torque_chrono)

    def bind_body(self, body: chrono.ChBody):
        body.AddForce(self.force_maker_chrono)
        body.AddForce(self.torque_maker_chrono)
        self.is_binded = True


CALLBACK_TYPE = Callable[[float, Any], ForceTorque]


class ForceControllerOnCallback(ForceControllerTemplate):

    def __init__(self, callback: CALLBACK_TYPE) -> None:
        super().__init__()
        self.callback = callback

    def get_force_torque(self, time: float, data) -> ForceTorque:
        return self.callback(time, data)


class YaxisShaker(ForceControllerTemplate):

    def __init__(self, amp: float = 5, amp_offset: float = 1, freq: float = 5) -> None:
        super().__init__()
        self.amp = amp
        self.amp_offset = amp_offset
        self.freq = freq

    def get_force_torque(self, time: float, data) -> ForceTorque:
        impact = ForceTorque()
        y_force = self.amp * sin(self.freq * time) + self.amp_offset
        impact.force = (0, y_force, 0)
        return impact


@dataclass
class ForceTorqueContainer:
    controller_list: list[ForceControllerTemplate] = field(default_factory=list)

    def update_all(self, time: float, data=None):
        for i in self.controller_list:
            i.update(time, data)

    def add(self, controller: ForceControllerTemplate):
        if controller.is_binded:
            self.controller_list.append(controller)
        else:
            raise Exception("Force controller should bind to body, before use")