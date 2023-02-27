from rostok.graph_grammar.node import BlockWrapper, ROOT
from rostok.graph_grammar import node_vocabulary, rule_vocabulary
from rostok.block_builder.node_render import *
from itertools import product
import pychrono as chrono

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def create_rules():

    def create_all_rules(base_name: str, in_nodes: list[str], out_nodes, in_edges, out_edges,
                         connections):
        for node in in_nodes:
            combinations = product(*out_nodes)
            for combination in combinations:
                rule_vocab.create_rule(
                    base_name + "_" + "".join([node]) + "->" + "".join(combination), [node],
                    list(combination), in_edges, out_edges, connections)

    length_link = [0.4, 0.6, 0.8]

    super_flat = BlockWrapper(FlatChronoBody, width_x=3, height_y=0.1, depth_z=3)
    link = list(map(lambda x: BlockWrapper(LinkChronoBody, length_y=x), length_link))
    u_1 = BlockWrapper(MountChronoBody, width_x=0.1, length_y=0.05)
    u_2 = BlockWrapper(MountChronoBody, width_x=0.2, length_y=0.1)
    radial_move_values = [0.9, 1.05, 1.2]
    RADIAL_MOVES = list(map(lambda x: FrameTransform([x, 0, 0], [1, 0, 0, 0]), radial_move_values))
    tan_move_values = [0.4, 0.6, 0.8]
    MOVES_POSITIVE = list(map(lambda x: FrameTransform([0, 0, x], [1, 0, 0, 0]),
                              tan_move_values))
    MOVES_NEGATIVE = list(
        map(lambda x: FrameTransform([0, 0, -x], [1, 0, 0, 0]), tan_move_values))

    def rotation_y(alpha):
        quat_Y_ang_alpha = chrono.Q_from_AngY(np.deg2rad(alpha))
        return [quat_Y_ang_alpha.e0, quat_Y_ang_alpha.e1, quat_Y_ang_alpha.e2, quat_Y_ang_alpha.e3]

    def rotation_z(alpha):
        quat_Z_ang_alpha = chrono.Q_from_AngZ(np.deg2rad(alpha))
        return [quat_Z_ang_alpha.e0, quat_Z_ang_alpha.e1, quat_Z_ang_alpha.e2, quat_Z_ang_alpha.e3]

    REVERSE_Y = FrameTransform([0, 0, 0], [0, 0, 1, 0])
    turn_const = 60
    TURN_P = FrameTransform([0,0,0],rotation_y(turn_const))
    TURN_N = FrameTransform([0,0,0],rotation_y(-turn_const))
    # MOVE = FrameTransform([1, 0, 0], rotation(45))
    radial_transform = list(map(lambda x: BlockWrapper(ChronoTransform, x), RADIAL_MOVES))
    positive_transforms = list(map(lambda x: BlockWrapper(ChronoTransform, x), MOVES_POSITIVE))
    negative_transforms = list(map(lambda x: BlockWrapper(ChronoTransform, x), MOVES_NEGATIVE))
    reverse_transform = BlockWrapper(ChronoTransform, REVERSE_Y)
    turn_transform_P = BlockWrapper(ChronoTransform, TURN_P)
    turn_transform_N = BlockWrapper(ChronoTransform, TURN_N)

    type_of_input = ChronoRevolveJoint.InputType.TORQUE
    revolve = BlockWrapper(ChronoRevolveJoint, ChronoRevolveJoint.Axis.Z, type_of_input)
    # Nodes
    node_vocab = node_vocabulary.NodeVocabulary()
    node_vocab.add_node(ROOT)
    node_vocab.create_node(label="F")
    node_vocab.create_node(label="J")
    node_vocab.create_node(label="RF")
    node_vocab.create_node(label="PF")
    node_vocab.create_node(label="NF")
    node_vocab.create_node(label="RPF")
    node_vocab.create_node(label="RNF")
    node_vocab.create_node(label="FT", is_terminal=True, block_wrapper=super_flat)
    node_vocab.create_node(label="RE", is_terminal=True, block_wrapper=reverse_transform)
    node_vocab.create_node(label="RT")
    node_vocab.create_node(label="RT1", is_terminal=True, block_wrapper=radial_transform[0])
    node_vocab.create_node(label="RT2", is_terminal=True, block_wrapper=radial_transform[1])
    node_vocab.create_node(label="RT3", is_terminal=True, block_wrapper=radial_transform[2])
    node_vocab.create_node(label="FG")
    # node_vocab.create_node(label="U1", is_terminal=True, block_wrapper=u_1)
    # node_vocab.create_node(label="U2", is_terminal=True, block_wrapper=u_2)
    #node_vocab.create_node(label="J1", is_terminal=True, block_wrapper=revolve)
    node_vocab.create_node(label="L")
    node_vocab.create_node(label="L1", is_terminal=True, block_wrapper=link[0])
    node_vocab.create_node(label="L2", is_terminal=True, block_wrapper=link[1])
    node_vocab.create_node(label="L3", is_terminal=True, block_wrapper=link[2])
    node_vocab.create_node(label="TP")
    node_vocab.create_node(label="TP1", is_terminal=True, block_wrapper=positive_transforms[0])
    node_vocab.create_node(label="TP2", is_terminal=True, block_wrapper=positive_transforms[1])
    node_vocab.create_node(label="TP3", is_terminal=True, block_wrapper=positive_transforms[2])
    node_vocab.create_node(label="TN")
    node_vocab.create_node(label="TN1", is_terminal=True, block_wrapper=negative_transforms[0])
    node_vocab.create_node(label="TN2", is_terminal=True, block_wrapper=negative_transforms[1])
    node_vocab.create_node(label="TN3", is_terminal=True, block_wrapper=negative_transforms[2])
    node_vocab.create_node(label="TURN_P", is_terminal=True, block_wrapper=turn_transform_P)
    node_vocab.create_node(label="TURN_N", is_terminal=True, block_wrapper=turn_transform_N)

    node_vocab.create_node(label="J1", is_terminal=True, block_wrapper=revolve)
    node_vocab.create_node(label="J2", is_terminal=True, block_wrapper=revolve)
    node_vocab.create_node(label="J3", is_terminal=True, block_wrapper=revolve)
    node_vocab.create_node(label="J4", is_terminal=True, block_wrapper=revolve)
    node_vocab.create_node(label="J5", is_terminal=True, block_wrapper=revolve)
    node_vocab.create_node(label="J6", is_terminal=True, block_wrapper=revolve)
    node_vocab.create_node(label="J7", is_terminal=True, block_wrapper=revolve)
    node_vocab.create_node(label="J8", is_terminal=True, block_wrapper=revolve)
    node_vocab.create_node(label="J9", is_terminal=True, block_wrapper=revolve)
    node_vocab.create_node(label="J10", is_terminal=True, block_wrapper=revolve)

    rule_vocab = rule_vocabulary.RuleVocabulary(node_vocab)
    rule_vocab.create_rule("Init", ["ROOT"], ["FT", "F", "RF", "PF", "NF", "RPF", "RNF"], 0, 0, [(0,1), (0,2), (0,3), (0,4), (0,5),(0, 6)])
    
    rule_vocab.create_rule("Phalanx", ["FG"], ["J", "L", "FG"], 0, 0, [(0, 1), (1, 2)])
    
    rule_vocab.create_rule("AddFinger", ["F"], [ "RT", "RE", "FG"], 0, 0, [(0, 1), (1, 2)])
    rule_vocab.create_rule("AddFinger_R", ["RF"], ["RE", "RT", "RE","FG"], 0, 0, [(0, 1), (1, 2), (2,3)])
    rule_vocab.create_rule("AddFinger_P", ["PF"], ["RT", "TP", "RE", "FG"], 0, 0, [(0, 1), (1, 2),
                                                                                  (2, 3)])
    rule_vocab.create_rule("AddFinger_PT", ["PF"], ["TURN_N","RT",  "RE", "FG"], 0, 0, [(0, 1), (1, 2),
                                                                                  (2, 3)])
    rule_vocab.create_rule("AddFinger_N", ["NF"], ["RT", "TN", "RE", "FG"], 0, 0, [(0, 1), (1, 2),
                                                                                  (2, 3)])
    rule_vocab.create_rule("AddFinger_NT", ["NF"], ["TURN_P","RT",  "RE", "FG"], 0, 0, [(0, 1), (1, 2),
                                                                                  (2, 3)])
    rule_vocab.create_rule("AddFinger_RP", ["RPF"], ["RE", "RT", "TP", "RE","FG"], 0, 0, [(0, 1), (1, 2),
                                                                                   (2, 3), (3, 4)])
    rule_vocab.create_rule("AddFinger_RPT", ["RPF"], ["RE", "TURN_N","RT",  "RE","FG"], 0, 0, [(0, 1), (1, 2),
                                                                                   (2, 3), (3, 4)])
    rule_vocab.create_rule("AddFinger_RN", ["RNF"], ["RE", "RT", "TN", "RE","FG"], 0, 0, [(0, 1), (1, 2),
                                                                                   (2, 3), (3, 4)])
    rule_vocab.create_rule("AddFinger_RNT", ["RNF"], ["RE", "TURN_P", "RT",  "RE","FG"], 0, 0, [(0, 1), (1, 2),
                                                                                   (2, 3), (3, 4)])
    
    rule_vocab.create_rule("RemoveFinger", ["F"], [], 0, 0, [])
    rule_vocab.create_rule("RemoveFinger_R", ["RF"], [], 0, 0, [])
    rule_vocab.create_rule("Remove_FG", ["FG"], [], 0, 0, [])
    rule_vocab.create_rule("RemoveFinger_P", ["PF"], [], 0, 0, [])
    rule_vocab.create_rule("RemoveFinger_N", ["NF"], [], 0, 0, [])
    rule_vocab.create_rule("RemoveFinger_RP", ["RPF"], [], 0, 0, [])
    rule_vocab.create_rule("RemoveFinger_RN", ["RNF"], [], 0, 0, [])
    
    rule_vocab.create_rule("Terminal_Radial_Translate1", ["RT"], ["RT1"], 0, 0, [])
    rule_vocab.create_rule("Terminal_Radial_Translate2", ["RT"], ["RT2"], 0, 0, [])
    
    rule_vocab.create_rule("Terminal_Link1", ["L"], ["L1"], 0, 0, [])
    rule_vocab.create_rule("Terminal_Link2", ["L"], ["L2"], 0, 0, [])
    rule_vocab.create_rule("Terminal_Link3", ["L"], ["L3"], 0, 0, [])
    
    rule_vocab.create_rule("Terminal_Joint1", ["J"], ["J1"], 0, 0, [])
    rule_vocab.create_rule("Terminal_Joint2", ["J"], ["J2"], 0, 0, [])
    rule_vocab.create_rule("Terminal_Joint3", ["J"], ["J3"], 0, 0, [])
    rule_vocab.create_rule("Terminal_Joint4", ["J"], ["J4"], 0, 0, [])
    rule_vocab.create_rule("Terminal_Joint5", ["J"], ["J5"], 0, 0, [])
    rule_vocab.create_rule("Terminal_Joint6", ["J"], ["J6"], 0, 0, [])
    rule_vocab.create_rule("Terminal_Joint7", ["J"], ["J7"], 0, 0, [])
    rule_vocab.create_rule("Terminal_Joint8", ["J"], ["J8"], 0, 0, [])
    rule_vocab.create_rule("Terminal_Joint9", ["J"], ["J9"], 0, 0, [])
    rule_vocab.create_rule("Terminal_Joint10", ["J"], ["J10"], 0, 0, [])
    
    rule_vocab.create_rule("Terminal_Positive_Translate1", ["TP"], ["TP1"], 0, 0, [])
    rule_vocab.create_rule("Terminal_Positive_Translate2", ["TP"], ["TP2"], 0, 0, [])
    rule_vocab.create_rule("Terminal_Negative_Translate1", ["TN"], ["TN1"], 0, 0, [])
    rule_vocab.create_rule("Terminal_Negative_Translate2", ["TN"], ["TN2"], 0, 0, [])
    torque_dict = {
        node_vocab.get_node("J1"): 1,
        node_vocab.get_node("J2"): 2,
        node_vocab.get_node("J3"): 3,
        node_vocab.get_node("J4"): 4,
        node_vocab.get_node("J5"): 5,
        node_vocab.get_node("J6"): 6,
        node_vocab.get_node("J7"): 7,
        node_vocab.get_node("J8"): 8,
        node_vocab.get_node("J9"): 9,
        node_vocab.get_node("J10"): 10
    }
    return rule_vocab, torque_dict


# if __name__ == "__main__":
#     rv, _ =create_rules()
#     print(rv)
#     print(rv.get_rule("Failed_Path").is_terminal)