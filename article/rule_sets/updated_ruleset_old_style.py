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

    super_flat = BlockWrapper(FlatChronoBody, width_x=3, height_y=0.05, depth_z=3)
    link = list(map(lambda x: BlockWrapper(LinkChronoBody, length_y=x), length_link))
    u_1 = BlockWrapper(MountChronoBody, width_x=0.1, length_y=0.05)
    u_2 = BlockWrapper(MountChronoBody, width_x=0.2, length_y=0.1)
    radial_move_values = [0.5, 1]
    RADIAL_MOVES = list(map(lambda x: FrameTransform([x, 0, 0], [1, 0, 0, 0]), radial_move_values))
    tan_move_values = [0.35, 0.6]
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
    node_vocab.create_node(label="FT", is_terminal=True, block_wrapper=super_flat)
    node_vocab.create_node(label="RE", is_terminal=True, block_wrapper=reverse_transform)
    node_vocab.create_node(label="RT")
    node_vocab.create_node(label="RT1", is_terminal=True, block_wrapper=radial_transform[0])
    node_vocab.create_node(label="RT2", is_terminal=True, block_wrapper=radial_transform[1])
    node_vocab.create_node(label="FG")
    node_vocab.create_node(label="U1", is_terminal=True, block_wrapper=u_1)
    node_vocab.create_node(label="U2", is_terminal=True, block_wrapper=u_2)
    node_vocab.create_node(label="J1", is_terminal=True, block_wrapper=revolve)
    node_vocab.create_node(label="L")
    node_vocab.create_node(label="L1", is_terminal=True, block_wrapper=link[0])
    node_vocab.create_node(label="L2", is_terminal=True, block_wrapper=link[1])
    node_vocab.create_node(label="L3", is_terminal=True, block_wrapper=link[2])
    node_vocab.create_node(label="TP")
    node_vocab.create_node(label="TP1", is_terminal=True, block_wrapper=positive_transforms[0])
    node_vocab.create_node(label="TP2", is_terminal=True, block_wrapper=positive_transforms[1])
    node_vocab.create_node(label="TN")
    node_vocab.create_node(label="TN1", is_terminal=True, block_wrapper=negative_transforms[0])
    node_vocab.create_node(label="TN2", is_terminal=True, block_wrapper=negative_transforms[1])
    node_vocab.create_node(label="TURN_P", is_terminal=True, block_wrapper=turn_transform_P)
    node_vocab.create_node(label="TURN_N", is_terminal=True, block_wrapper=turn_transform_N)

    rule_vocab = rule_vocabulary.RuleVocabulary(node_vocab)
    rule_vocab.create_rule("Init", ["ROOT"], ["F"], 0, 0, [])
    rule_vocab.create_rule("TerminalFlat", ["F"], ["FT"], 0, 0, [])
    rule_vocab.create_rule("AddFinger", ["F"], ["F", "RT", "RE", "FG"], 0, 0, [(0, 1), (1, 2), (2,3)])
    rule_vocab.create_rule("AddFinger_R", ["F"], ["F","RE", "RT", "RE","FG"], 0, 0, [(0, 1), (1, 2), (2,3),(3,4)])
    rule_vocab.create_rule("Terminal_Radial_Translate1", ["RT"], ["RT1"], 0, 0, [])
    rule_vocab.create_rule("Terminal_Radial_Translate2", ["RT"], ["RT2"], 0, 0, [])
    rule_vocab.create_rule("Phalanx", ["FG"], ["J1", "L", "FG"], 0, 0, [(0, 1), (1, 2)])
    rule_vocab.create_rule("Terminal_Link1", ["L"], ["L1"], 0, 0, [])
    rule_vocab.create_rule("Terminal_Link2", ["L"], ["L2"], 0, 0, [])
    rule_vocab.create_rule("Terminal_Link3", ["L"], ["L3"], 0, 0, [])
    rule_vocab.create_rule("Terminal_EF1", ["FG"], ["U1"], 0, 0, [])
    rule_vocab.create_rule("Terminal_EF2", ["FG"], ["U2"], 0, 0, [])
    rule_vocab.create_rule("AddFinger_P", ["F"], ["F","RT", "TP", "RE", "FG"], 0, 0, [(0, 1), (1, 2),
                                                                                  (2, 3), (3, 4)])
    rule_vocab.create_rule("AddFinger_PT", ["F"], ["F","RT", "TP", "TURN_N","RE", "FG"], 0, 0, [(0, 1), (1, 2),
                                                                                  (2, 3), (3, 4), (4,5)])
    rule_vocab.create_rule("AddFinger_N", ["F"], ["F","RT", "TN", "RE", "FG"], 0, 0, [(0, 1), (1, 2),
                                                                                  (2, 3), (3, 4)])
    rule_vocab.create_rule("AddFinger_NT", ["F"], ["F","RT", "TN", "TURN_P","RE", "FG"], 0, 0, [(0, 1), (1, 2),
                                                                                  (2, 3), (3, 4), (4,5)])
    rule_vocab.create_rule("AddFinger_RP", ["F"], ["F","RE", "RT", "TP", "RE","FG"], 0, 0, [(0, 1), (1, 2),
                                                                                   (2, 3), (3, 4),(4,5)])
    rule_vocab.create_rule("AddFinger_RPT", ["F"], ["F","RE", "RT", "TP", "TURN_N","RE","FG"], 0, 0, [(0, 1), (1, 2),
                                                                                   (2, 3), (3, 4),(4,5),(5,6)])
    rule_vocab.create_rule("AddFinger_RN", ["F"], ["F","RE", "RT", "TN", "RE","FG"], 0, 0, [(0, 1), (1, 2),
                                                                                   (2, 3), (3, 4),(4,5)])
    rule_vocab.create_rule("AddFinger_RNT", ["F"], ["F","RE", "RT", "TN", "TURN_P", "RE","FG"], 0, 0, [(0, 1), (1, 2),
                                                                                   (2, 3), (3, 4),(4,5), (5,6)])
    rule_vocab.create_rule("Terminal_Positive_Translate1", ["TP"], ["TP1"], 0, 0, [])
    rule_vocab.create_rule("Terminal_Positive_Translate2", ["TP"], ["TP2"], 0, 0, [])
    rule_vocab.create_rule("Terminal_Negative_Translate1", ["TN"], ["TN1"], 0, 0, [])
    rule_vocab.create_rule("Terminal_Negative_Translate2", ["TN"], ["TN2"], 0, 0, [])

    rule_vocab.get_rule("AddFinger").is_sigleton = True
    rule_vocab.get_rule("AddFinger_R").is_sigleton = True
    rule_vocab.get_rule("AddFinger_P").is_sigleton = True
    rule_vocab.get_rule("AddFinger_P").rule_class = "P"
    rule_vocab.get_rule("AddFinger_PT").is_sigleton = True
    rule_vocab.get_rule("AddFinger_PT").rule_class = "P"
    rule_vocab.get_rule("AddFinger_N").is_sigleton = True
    rule_vocab.get_rule("AddFinger_N").rule_class = "N"
    rule_vocab.get_rule("AddFinger_NT").is_sigleton = True
    rule_vocab.get_rule("AddFinger_NT").rule_class = "N"
    rule_vocab.get_rule("AddFinger_RP").is_sigleton = True
    rule_vocab.get_rule("AddFinger_RP").is_sigleton = "RP"
    rule_vocab.get_rule("AddFinger_RPT").is_sigleton = True
    rule_vocab.get_rule("AddFinger_RPT").is_sigleton = "RP"
    rule_vocab.get_rule("AddFinger_RN").is_sigleton = True
    rule_vocab.get_rule("AddFinger_RN").is_sigleton = "RN"
    rule_vocab.get_rule("AddFinger_RNT").is_sigleton = True
    rule_vocab.get_rule("AddFinger_RNT").is_sigleton = "RN"

    return rule_vocab


# if __name__ == "__main__":
#     rv, _ =create_rules()
#     print(rv)
#     print(rv.get_rule("Failed_Path").is_terminal)
