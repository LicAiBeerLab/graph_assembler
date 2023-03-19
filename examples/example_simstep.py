import random

import numpy as np
import pychrono as chrono
from example_vocabulary import (get_terminal_graph_no_joints, get_terminal_graph_three_finger,
                                get_terminal_graph_two_finger)

import rostok.virtual_experiment.simulation_step as step
from rostok.block_builder.envbody_shapes import Box
from rostok.block_builder.node_render import (ChronoBodyEnv, DefaultChronoMaterial, FrameTransform)
from rostok.virtual_experiment.flags_simualtions import FlagMaxTime
from rostok.graph_grammar.node import BlockWrapper
from rostok.trajectory_optimizer.control_optimizer import num_joints
from rostok.trajectory_optimizer.trajectory_generator import \
    create_torque_traj_from_x
from rostok.graph_grammar.graph_utils import plot_graph

mechs = [
    get_terminal_graph_three_finger, get_terminal_graph_no_joints, get_terminal_graph_two_finger
]
for get_graph in mechs:
    # Constants
    MAX_TIME = 1
    TIME_STEP = 1e-3

    graph = get_graph()
    # Create trajectory
    number_trq = num_joints(graph)
    const_torque_koef = [random.random() for _ in range(number_trq)]
    arr_trj = create_torque_traj_from_x(graph, const_torque_koef, MAX_TIME, TIME_STEP)

    # Create object to grasp
    mat = DefaultChronoMaterial()
    mat.Friction = 0.65
    mat.DampingF = 0.65
    obj = BlockWrapper(ChronoBodyEnv,
                       shape=Box(),
                       material=mat,
                       pos=FrameTransform([0, 1, 0], [0, -0.048, 0.706, 0.706]))

    # Configurate simulation
    config_sys = {"Set_G_acc": chrono.ChVectorD(0, 0, 0)}
    flags = [FlagMaxTime(MAX_TIME)]

    sim = step.SimulationStepOptimization(arr_trj, graph, obj,
                                          FrameTransform([0, 1.5, 0], [0, 1, 0, 0]))
    sim.set_flags_stop_simulation(flags)
    sim.change_config_system(config_sys)

    # Start simulation
    sim_output = sim.simulate_system(TIME_STEP, True)
