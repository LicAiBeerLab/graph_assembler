import sys
import time
from datetime import datetime
from pathlib import Path

import hyperparameters as hp
import matplotlib.pyplot as plt
import mcts
import numpy as np
from mcts_run_setup import config_with_const_troques, config_with_tendon, config_combination_force_tendon_multiobject

from rostok.graph_grammar.node import GraphGrammar
from rostok.library.obj_grasp.objects import (get_object_ellipsoid, get_object_parametrized_sphere,
                                              get_object_parametrized_sphere_smc)
from rostok.library.rule_sets.ruleset_old_style_smc import create_rules
from rostok.library.rule_sets.simple_designs import (
    get_four_same_link_one_finger, get_one_finger_one_link, get_one_finger_one_nlink,
    get_one_finger_one_plink, get_one_finger_one_rplink, get_one_finger_one_nplink,
    get_three_link_one_finger, get_three_same_link_one_finger, get_two_link_three_finger,
    get_two_same_link_one_finger)
from rostok.simulation_chrono.basic_simulation import SimulationResult

# create blueprint for object to grasp
grasp_object_blueprint = get_object_parametrized_sphere(0.01)
#grasp_object_blueprint = get_object_ellipsoid(10, 8, 14, 10)

# create reward counter using run setup function
control_optimizer = config_with_const_troques(grasp_object_blueprint)
control_optimizer = config_combination_force_tendon_multiobject([grasp_object_blueprint], [1])

print("Object to grasp:", grasp_object_blueprint.shape)
dict = {
    item: getattr(hp, item)
    for item in dir(hp)
    if not item.startswith("__") and not item.endswith("__")
}
for key, value in dict.items():
    print(key, value)
simulation_rewarder = control_optimizer.rewarder
simulation_manager = control_optimizer.simulation_scenario

graph = get_three_link_one_finger()
#graph=get_two_link_three_finger()
graph = get_three_same_link_one_finger()
#graph = get_two_same_link_one_finger()
#graph=get_four_same_link_one_finger()
#graph = get_one_finger_one_link()
#graph = get_one_finger_one_nplink()
#graph=get_two_link_three_finger()
# graph=get_one_finger_one_link()

control = [[30]]

data = control_optimizer.optim_parameters2data_control(control, graph)[0]

vis = True
#simulation_output: SimulationResult = simulation_manager.run_simulation(graph, data, [[-45.0, 0.0],[-45,0],[-45,0]], vis, True)
simulation_output: SimulationResult = simulation_manager[0][0].run_simulation(
    graph, data, [[-45, 0, 0]], vis, True)

res = simulation_rewarder.calculate_reward(simulation_output)
print('reward', res)