import hyperparameters as hp

from rostok.criterion.flags_simualtions import (FlagMaxTime, FlagNotContact, FlagSlipout)
from rostok.trajectory_optimizer.trajectory_generator import \
    create_torque_traj_from_x, create_control_from_graph, create_step_torque_traj_from_x

from rostok.criterion.criterion_calc import criterion_calc
from functools import partial
from rostok.trajectory_optimizer.control_optimizer import ConfigVectorJoints, ConfigGraphControl
from rostok.graph_grammar.node import Node
from scipy.optimize import dual_annealing
from rostok.graph_grammar.node import GraphGrammar
""" All config without get_rgab_object_callback"""



def create_traj_fun_graph(stop_time: float, time_step: float, torque_dict):

    def fun(graph: GraphGrammar, x: list[float]):
        return create_control_from_graph(graph, torque_dict, stop_time, time_step)

    return fun

def get_cfg_standart():
    WEIGHT = hp.CRITERION_WEIGHTS
    # Init configuration of control optimizing
    cfg = ConfigVectorJoints()
    cfg.bound = (6, 15)
    cfg.iters = hp.CONTROL_OPTIMIZATION_ITERATION
    cfg.time_step = hp.TIME_STEP_SIMULATION
    cfg.time_sim = hp.TIME_SIMULATION
    cfg.flags = [FlagMaxTime(cfg.time_sim), 
                 FlagNotContact(hp.FLAG_TIME_NO_CONTACT), 
                 FlagSlipout(hp.FLAG_TIME_NO_CONTACT, hp.FLAG_TIME_SLIPOUT)]
    """Wraps function call"""
    criterion_callback = partial(criterion_calc, weights=WEIGHT)
    traj_generator_fun = partial(create_torque_traj_from_x,
                                 stop_time=cfg.time_sim,
                                 time_step=cfg.time_step)

    cfg.criterion_callback = criterion_callback
    cfg.params_to_timesiries_callback = traj_generator_fun
    return cfg


def get_cfg_graph(torque_dict: dict[Node, float]):
    WEIGHT = hp.CRITERION_WEIGHTS
    # Init configuration of control optimizing
    cfg = ConfigGraphControl()
    cfg.time_step = hp.TIME_STEP_SIMULATION
    cfg.time_sim = hp.TIME_SIMULATION
    cfg.flags = [FlagMaxTime(cfg.time_sim), 
                 FlagNotContact(hp.FLAG_TIME_NO_CONTACT), 
                 FlagSlipout(hp.FLAG_TIME_NO_CONTACT, hp.FLAG_TIME_SLIPOUT)]
    """Wraps function call"""
    criterion_callback = partial(criterion_calc, weights=WEIGHT)
    traj_generator_fun = create_traj_fun_graph(cfg.time_sim, cfg.time_step, torque_dict)

    cfg.criterion_callback = criterion_callback
    cfg.params_to_timesiries_callback = traj_generator_fun
    return cfg


def get_cfg_standart_anealing():
    WEIGHT = hp.CRITERION_WEIGHTS
    # Init configuration of control optimizing
    cfg = ConfigVectorJoints()
    cfg.optimizer_scipy = partial(dual_annealing)
    cfg.bound = (6, 15)
    cfg.iters = hp.CONTROL_OPTIMIZATION_ITERATION
    cfg.time_step = hp.TIME_STEP_SIMULATION
    cfg.time_sim = hp.TIME_SIMULATION
    cfg.flags = [FlagMaxTime(cfg.time_sim), 
                 FlagNotContact(hp.FLAG_TIME_NO_CONTACT), 
                 FlagSlipout(hp.FLAG_TIME_NO_CONTACT, hp.FLAG_TIME_SLIPOUT)]
    """Wraps function call"""
    criterion_callback = partial(criterion_calc, weights=WEIGHT)
    traj_generator_fun = partial(create_torque_traj_from_x,
                                 stop_time=cfg.time_sim,
                                 time_step=cfg.time_step)

    cfg.criterion_callback = criterion_callback
    cfg.params_to_timesiries_callback = traj_generator_fun
    return cfg


def get_cfg_standart_step():
    WEIGHT = hp.CRITERION_WEIGHTS
    # Init configuration of control optimizing
    CONST_TORQUE = 12
    cfg = ConfigVectorJoints()
    cfg.bound = (0, hp.TIME_SIMULATION / 3)
    cfg.iters = hp.CONTROL_OPTIMIZATION_ITERATION
    cfg.time_step = hp.TIME_STEP_SIMULATION
    cfg.time_sim = hp.TIME_SIMULATION
    cfg.flags = [FlagMaxTime(cfg.time_sim), 
                 FlagNotContact(hp.FLAG_TIME_NO_CONTACT), 
                 FlagSlipout(hp.FLAG_TIME_NO_CONTACT, hp.FLAG_TIME_SLIPOUT)]
    """Wraps function call"""
    criterion_callback = partial(criterion_calc, weights=WEIGHT)
    traj_generator_fun = partial(create_step_torque_traj_from_x,
                                 stop_time=cfg.time_sim,
                                 time_step=cfg.time_step,
                                 torque = CONST_TORQUE)

    cfg.criterion_callback = criterion_callback
    cfg.params_to_timesiries_callback = traj_generator_fun
    return cfg



def get_cfg_small_iter_standart():
    WEIGHT = hp.CRITERION_WEIGHTS
    # Init configuration of control optimizing
    cfg = ConfigVectorJoints()
    cfg.bound = (6, 15)
    cfg.time_optimization = hp.TIME_OPTIMIZATION
    cfg.iters = 10
    cfg.time_step = hp.TIME_STEP_SIMULATION
    cfg.time_sim = hp.TIME_SIMULATION
    cfg.flags = [FlagMaxTime(cfg.time_sim), 
                 FlagNotContact(hp.FLAG_TIME_NO_CONTACT), 
                 FlagSlipout(hp.FLAG_TIME_NO_CONTACT, hp.FLAG_TIME_SLIPOUT)]
    """Wraps function call"""
    criterion_callback = partial(criterion_calc, weights=WEIGHT)
    traj_generator_fun = partial(create_torque_traj_from_x,
                                 stop_time=cfg.time_sim,
                                 time_step=cfg.time_step)

    cfg.criterion_callback = criterion_callback
    cfg.params_to_timesiries_callback = traj_generator_fun
    return cfg