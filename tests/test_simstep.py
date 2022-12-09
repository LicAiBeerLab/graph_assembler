import random

import numpy as np
import pychrono as chrono
from test_ruleset import (get_terminal_graph_ladoshaka,
                          get_terminal_graph_three_finger,
                          get_terminal_graph_two_finger)

import app.app_vocabulary as voca
import rostok.virtual_experiment.simulation_step as step
from rostok.criterion.flags_simualtions import FlagMaxTime
from rostok.trajectory_optimizer.control_optimizer import num_joints
from rostok.trajectory_optimizer.trajectory_generator import (
    create_dfs_joint, create_torque_traj_from_x)


def test_create_graph():
    """
        Test for graph grammar and rule
    """
    graph = voca.get_random_graph(5, voca.app_rule_vocab)


def test_control_bind_and_create_sim():
    """
        Test for simulation class, control binder and control generator
    """
    
    mechs = [get_terminal_graph_three_finger,
            get_terminal_graph_ladoshaka, get_terminal_graph_two_finger]

    for get_graph in mechs:
        G = get_graph()
        number_trq = num_joints(G)

        config_sys = {"Set_G_acc": chrono.ChVectorD(0, 0, 0)}
        max_time = 1
        flags = [FlagMaxTime(max_time)]
        times_step = 1e-3

        const_torque_koef = [random.random() for _ in range(number_trq)]
        arr_trj = create_torque_traj_from_x(G, const_torque_koef, 1, 0.1)

        grab_obj_mat = chrono.ChMaterialSurfaceNSC()
        grab_obj_mat.SetFriction(0.5)
        grab_obj_mat.SetDampingF(0.1)
        obj = chrono.ChBodyEasyBox(0.2, 0.2, 0.6, 1000, True, True, grab_obj_mat)
        obj.SetCollide(True)
        obj.SetPos(chrono.ChVectorD(0, 1.2, 0))

        sim = step.SimulationStepOptimization(arr_trj, G, obj)
        sim.set_flags_stop_simulation(flags)
        sim.change_config_system(config_sys)
        sim_output = sim.simulate_system(times_step)