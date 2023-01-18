from rostok.graph_grammar.node import GraphGrammar, BlockWrapper, ROOT, Node
from rostok.block_builder.basic_node_block import SimpleBody
from rostok.block_builder.node_render import DefaultChronoMaterial
from rostok.block_builder.transform_srtucture import FrameTransform, rotation
from rostok.block_builder.node_render import (LinkChronoBody, MountChronoBody, ChronoTransform,
                                              ChronoRevolveJoint, FlatChronoBody, ChronoBodyEnv)
import rostok.graph_grammar.node_vocabulary as node_vocabulary
import rostok.graph_grammar.rule_vocabulary as rule_vocabulary
import rostok.criterion.criterion_calc as criterion
from rostok.trajectory_optimizer.trajectory_generator import \
    create_torque_traj_from_x
from rostok.virtual_experiment.simulation_step import SimOut


def get_234_fingers_mechanism_rules(width_flats: list[float], length_links: list[float]):
    """Creating standard rules: creating palm with 2/3/4 fingers, adding phalanx to mount and terminating node.
    The function returns the rule_vocabulary is object of :py:class:`rule_vocabulary.RuleVocabulary` class.
    It can manipulate vocabulary rules. Adding new rules or return (non)terminal rules. See description to :py:module:`rostock.graph_grammar.rule_vocabulary`
    Current, supporting exactly three different width_flats and length_links.

    Args:
        width_flats (list[float]): List of desired flats(palms) width. It has exactly three flat widths
        length_links (list[float]): List of desired phalanx lengths. It has exactly three link lengths

    Returns:
        tuple: Tuple have two elements: rule_vocabulary(`rule_vocabulary.RuleVocabulary`) and node_features for correct calculate grab criterion.
    """
    if len(width_flats) != 3 or len(length_links) != 3:
        raise Exception(
            "Read the description. In the current version, you need to add exactly three list items"
        )
    # %% Bodies for extansions rules
    links = list(map(lambda x: BlockWrapper(LinkChronoBody, length=x), length_links))

    flats = list(map(lambda x: BlockWrapper(FlatChronoBody, width=x), width_flats))

    u1 = BlockWrapper(MountChronoBody, width=0.1, length=0.05)
    u2 = BlockWrapper(MountChronoBody, width=0.2, length=0.1)

    MOVE_TO_RIGHT_SIDE = map(lambda x: FrameTransform([x, 0, 0], [0, 0, 1, 0]), width_flats)
    MOVE_TO_RIGHT_SIDE_PLUS = map(lambda x: FrameTransform([x, 0, +0.3], [0, 0, 1, 0]), width_flats)
    MOVE_TO_RIGHT_SIDE_PLUS_ANGLE = map(lambda x: FrameTransform([x, 0, +0.3], rotation(150)),
                                        width_flats)
    MOVE_TO_RIGHT_SIDE_MINUS = map(lambda x: FrameTransform([x, 0, -0.3], [0, 0, 1, 0]),
                                   width_flats)
    MOVE_TO_RIGHT_SIDE_MINUS_ANGLE = map(lambda x: FrameTransform([x, 0, -0.3], rotation(210)),
                                         width_flats)
    MOVE_TO_LEFT_SIDE = map(lambda x: FrameTransform([-x, 0, 0], [1, 0, 0, 0]), width_flats)
    MOVE_TO_LEFT_SIDE_PLUS = map(lambda x: FrameTransform([-x, 0, +0.3], [1, 0, 0, 0]), width_flats)
    MOVE_TO_LEFT_SIDE_PLUS_ANGLE = map(lambda x: FrameTransform([-x, 0, +0.3], rotation(30)),
                                       width_flats)
    MOVE_TO_LEFT_SIDE_MINUS = map(lambda x: FrameTransform([-x, 0, -0.3], [1, 0, 0, 0]),
                                  width_flats)
    MOVE_TO_LEFT_SIDE_MINUS_ANGLE = map(lambda x: FrameTransform([-x, 0, -0.3], rotation(-30)),
                                        width_flats)

    transform_to_right_mount = list(
        map(lambda x: BlockWrapper(ChronoTransform, x), MOVE_TO_RIGHT_SIDE))
    transform_to_right_mount_plus = list(
        map(lambda x: BlockWrapper(ChronoTransform, x), MOVE_TO_RIGHT_SIDE_PLUS))
    transform_to_right_mount_plus_angle = list(
        map(lambda x: BlockWrapper(ChronoTransform, x), MOVE_TO_RIGHT_SIDE_PLUS_ANGLE))
    transform_to_right_mount_minus = list(
        map(lambda x: BlockWrapper(ChronoTransform, x), MOVE_TO_RIGHT_SIDE_MINUS))
    transform_to_right_mount_minus_angle = list(
        map(lambda x: BlockWrapper(ChronoTransform, x), MOVE_TO_RIGHT_SIDE_MINUS_ANGLE))
    transform_to_left_mount = list(
        map(lambda x: BlockWrapper(ChronoTransform, x), MOVE_TO_LEFT_SIDE))
    transform_to_left_mount_plus = list(
        map(lambda x: BlockWrapper(ChronoTransform, x), MOVE_TO_LEFT_SIDE_PLUS))
    transform_to_left_mount_plus_angle = list(
        map(lambda x: BlockWrapper(ChronoTransform, x), MOVE_TO_LEFT_SIDE_PLUS_ANGLE))
    transform_to_left_mount_minus = list(
        map(lambda x: BlockWrapper(ChronoTransform, x), MOVE_TO_LEFT_SIDE_MINUS))
    transform_to_left_mount_minus_angle = list(
        map(lambda x: BlockWrapper(ChronoTransform, x), MOVE_TO_LEFT_SIDE_MINUS_ANGLE))
    # transform_to_alpha_rotate = BlockWrapper(ChronoTransform, ROTATE_TO_ALPHA)

    # %%
    type_of_input = ChronoRevolveJoint.InputType.TORQUE

    # Joints
    revolve1 = BlockWrapper(ChronoRevolveJoint, ChronoRevolveJoint.Axis.Z, type_of_input)

    # Nodes
    node_vocab = node_vocabulary.NodeVocabulary()
    node_vocab.add_node(ROOT)
    node_vocab.create_node("J")
    node_vocab.create_node("L")
    node_vocab.create_node("F")
    node_vocab.create_node("M")
    node_vocab.create_node("EF")
    node_vocab.create_node("EM")
    node_vocab.create_node("SML")
    node_vocab.create_node("SMR")
    node_vocab.create_node("SMRP")
    node_vocab.create_node("SMRPA")
    node_vocab.create_node("SMLP")
    node_vocab.create_node("SMLPA")
    node_vocab.create_node("SMRM")
    node_vocab.create_node("SMRMA")
    node_vocab.create_node("SMLM")
    node_vocab.create_node("SMLMA")

    node_vocab.create_node(label="J1", is_terminal=True, block_wrapper=revolve1)

    link_labels = []
    for idx, link in enumerate(links):
        link_labels.append("L" + str(idx + 1))
        node_vocab.create_node(label=link_labels[-1], is_terminal=True, block_wrapper=link)

    flat_labels = []
    for idx, flat in enumerate(flats):
        flat_labels.append("F" + str(idx + 1))
        node_vocab.create_node(label=flat_labels[-1], is_terminal=True, block_wrapper=flat)

    node_vocab.create_node(label="U1", is_terminal=True, block_wrapper=u1)
    node_vocab.create_node(label="U2", is_terminal=True, block_wrapper=u2)

    node_vocab.create_node(label="TR1", is_terminal=True, block_wrapper=transform_to_right_mount[0])
    node_vocab.create_node(label="TR2", is_terminal=True, block_wrapper=transform_to_right_mount[1])
    node_vocab.create_node(label="TR3", is_terminal=True, block_wrapper=transform_to_right_mount[2])
    node_vocab.create_node(label="TRP1",
                           is_terminal=True,
                           block_wrapper=transform_to_right_mount_plus[0])
    node_vocab.create_node(label="TRP2",
                           is_terminal=True,
                           block_wrapper=transform_to_right_mount_plus[1])
    node_vocab.create_node(label="TRP3",
                           is_terminal=True,
                           block_wrapper=transform_to_right_mount_plus[2])
    node_vocab.create_node(label="TRPA1",
                           is_terminal=True,
                           block_wrapper=transform_to_right_mount_plus_angle[0])
    node_vocab.create_node(label="TRPA2",
                           is_terminal=True,
                           block_wrapper=transform_to_right_mount_plus_angle[1])
    node_vocab.create_node(label="TRPA3",
                           is_terminal=True,
                           block_wrapper=transform_to_right_mount_plus_angle[2])
    node_vocab.create_node(label="TRM1",
                           is_terminal=True,
                           block_wrapper=transform_to_right_mount_minus[0])
    node_vocab.create_node(label="TRM2",
                           is_terminal=True,
                           block_wrapper=transform_to_right_mount_minus[1])
    node_vocab.create_node(label="TRM3",
                           is_terminal=True,
                           block_wrapper=transform_to_right_mount_minus[2])
    node_vocab.create_node(label="TRMA1",
                           is_terminal=True,
                           block_wrapper=transform_to_right_mount_minus_angle[0])
    node_vocab.create_node(label="TRMA2",
                           is_terminal=True,
                           block_wrapper=transform_to_right_mount_minus_angle[1])
    node_vocab.create_node(label="TRMA3",
                           is_terminal=True,
                           block_wrapper=transform_to_right_mount_minus_angle[2])

    node_vocab.create_node(label="TL1", is_terminal=True, block_wrapper=transform_to_left_mount[0])
    node_vocab.create_node(label="TL2", is_terminal=True, block_wrapper=transform_to_left_mount[1])
    node_vocab.create_node(label="TL3", is_terminal=True, block_wrapper=transform_to_left_mount[2])
    node_vocab.create_node(label="TLP1",
                           is_terminal=True,
                           block_wrapper=transform_to_left_mount_plus[0])
    node_vocab.create_node(label="TLP2",
                           is_terminal=True,
                           block_wrapper=transform_to_left_mount_plus[1])
    node_vocab.create_node(label="TLP3",
                           is_terminal=True,
                           block_wrapper=transform_to_left_mount_plus[2])
    node_vocab.create_node(label="TLPA1",
                           is_terminal=True,
                           block_wrapper=transform_to_left_mount_plus_angle[0])
    node_vocab.create_node(label="TLPA2",
                           is_terminal=True,
                           block_wrapper=transform_to_left_mount_plus_angle[1])
    node_vocab.create_node(label="TLPA3",
                           is_terminal=True,
                           block_wrapper=transform_to_left_mount_plus_angle[2])
    node_vocab.create_node(label="TLM1",
                           is_terminal=True,
                           block_wrapper=transform_to_left_mount_minus[0])
    node_vocab.create_node(label="TLM2",
                           is_terminal=True,
                           block_wrapper=transform_to_left_mount_minus[1])
    node_vocab.create_node(label="TLM3",
                           is_terminal=True,
                           block_wrapper=transform_to_left_mount_minus[2])
    node_vocab.create_node(label="TLMA1",
                           is_terminal=True,
                           block_wrapper=transform_to_left_mount_minus_angle[0])
    node_vocab.create_node(label="TLMA2",
                           is_terminal=True,
                           block_wrapper=transform_to_left_mount_minus_angle[1])
    node_vocab.create_node(label="TLMA3",
                           is_terminal=True,
                           block_wrapper=transform_to_left_mount_minus_angle[2])

    # Defines rules
    rule_vocab = rule_vocabulary.RuleVocabulary(node_vocab)

    rule_vocab.create_rule("InitMechanism_2", ["ROOT"], ["F", "SML", "SMR", "EM", "EM"], 0, 0,
                           [(0, 1), (0, 2), (1, 3), (2, 4)])
    rule_vocab.create_rule("InitMechanism_3_R", ["ROOT"],
                           ["F", "SML", "SMRP", "SMRM", "EM", "EM", "EM"], 0, 0, [(0, 1), (0, 2),
                                                                                  (0, 3), (1, 4),
                                                                                  (2, 5), (3, 6)])
    rule_vocab.create_rule("InitMechanism_3_R_A", ["ROOT"],
                           ["F", "SML", "SMRPA", "SMRMA", "EM", "EM", "EM"], 0, 0, [(0, 1), (0, 2),
                                                                                    (0, 3), (1, 4),
                                                                                    (2, 5), (3, 6)])
    rule_vocab.create_rule("InitMechanism_3_L", ["ROOT"],
                           ["F", "SMLP", "SMLM", "SMR", "EM", "EM", "EM"], 0, 0, [(0, 1), (0, 2),
                                                                                  (0, 3), (1, 4),
                                                                                  (2, 5), (3, 6)])
    rule_vocab.create_rule("InitMechanism_3_L_A", ["ROOT"],
                           ["F", "SMLPA", "SMLMA", "SMR", "EM", "EM", "EM"], 0, 0, [(0, 1), (0, 2),
                                                                                    (0, 3), (1, 4),
                                                                                    (2, 5), (3, 6)])
    rule_vocab.create_rule("FingerUpper", ["EM"], ["J", "L", "EM"], 0, 2, [(0, 1), (1, 2)])

    rule_vocab.create_rule("TerminalFlat1", ["F"], ["F1"], 0, 0)
    rule_vocab.create_rule("TerminalFlat2", ["F"], ["F2"], 0, 0)
    rule_vocab.create_rule("TerminalFlat3", ["F"], ["F3"], 0, 0)

    rule_vocab.create_rule("TerminalL1", ["L"], ["L1"], 0, 0)
    rule_vocab.create_rule("TerminalL2", ["L"], ["L2"], 0, 0)
    rule_vocab.create_rule("TerminalL3", ["L"], ["L3"], 0, 0)

    rule_vocab.create_rule("TerminalTransformRight1", ["SMR"], ["TR1"], 0, 0)
    rule_vocab.create_rule("TerminalTransformRight2", ["SMR"], ["TR2"], 0, 0)
    rule_vocab.create_rule("TerminalTransformRight3", ["SMR"], ["TR3"], 0, 0)

    rule_vocab.create_rule("TerminalTransformRightPlus1", ["SMRP"], ["TRP1"], 0, 0)
    rule_vocab.create_rule("TerminalTransformRightPlus2", ["SMRP"], ["TRP2"], 0, 0)
    rule_vocab.create_rule("TerminalTransformRightPlus3", ["SMRP"], ["TRP3"], 0, 0)

    rule_vocab.create_rule("TerminalTransformRightPlusAngle1", ["SMRPA"], ["TRPA1"], 0, 0)
    rule_vocab.create_rule("TerminalTransformRightPlusAngle2", ["SMRPA"], ["TRPA2"], 0, 0)
    rule_vocab.create_rule("TerminalTransformRightPlusAngle3", ["SMRPA"], ["TRPA3"], 0, 0)

    rule_vocab.create_rule("TerminalTransformRightMinus1", ["SMRM"], ["TRM1"], 0, 0)
    rule_vocab.create_rule("TerminalTransformRightMinus2", ["SMRM"], ["TRM2"], 0, 0)
    rule_vocab.create_rule("TerminalTransformRightMinus3", ["SMRM"], ["TRM3"], 0, 0)

    rule_vocab.create_rule("TerminalTransformRightMinusAngle1", ["SMRMA"], ["TRMA1"], 0, 0)
    rule_vocab.create_rule("TerminalTransformRightMinusAngle2", ["SMRMA"], ["TRMA2"], 0, 0)
    rule_vocab.create_rule("TerminalTransformRightMinusAngle3", ["SMRMA"], ["TRMA3"], 0, 0)

    rule_vocab.create_rule("TerminalTransformLeft1", ["SML"], ["TL1"], 0, 0)
    rule_vocab.create_rule("TerminalTransformLeft2", ["SML"], ["TL2"], 0, 0)
    rule_vocab.create_rule("TerminalTransformLeft3", ["SML"], ["TL3"], 0, 0)

    rule_vocab.create_rule("TerminalTransformLeftPlus1", ["SMLP"], ["TLP1"], 0, 0)
    rule_vocab.create_rule("TerminalTransformLeftPlus2", ["SMLP"], ["TLP2"], 0, 0)
    rule_vocab.create_rule("TerminalTransformLeftPlus3", ["SMLP"], ["TLP3"], 0, 0)

    rule_vocab.create_rule("TerminalTransformLeftPlusAngle1", ["SMLPA"], ["TLPA1"], 0, 0)
    rule_vocab.create_rule("TerminalTransformLeftPlusAngle2", ["SMLPA"], ["TLPA2"], 0, 0)
    rule_vocab.create_rule("TerminalTransformLeftPlusAngle3", ["SMLPA"], ["TLPA3"], 0, 0)

    rule_vocab.create_rule("TerminalTransformLeftMinus1", ["SMLM"], ["TLM1"], 0, 0)
    rule_vocab.create_rule("TerminalTransformLeftMinus2", ["SMLM"], ["TLM2"], 0, 0)
    rule_vocab.create_rule("TerminalTransformLeftMinus3", ["SMLM"], ["TLM3"], 0, 0)

    rule_vocab.create_rule("TerminalTransformLeftMinusAngle1", ["SMLMA"], ["TLMA1"], 0, 0)
    rule_vocab.create_rule("TerminalTransformLeftMinusAngle2", ["SMLMA"], ["TLMA2"], 0, 0)
    rule_vocab.create_rule("TerminalTransformLeftMinusAngle3", ["SMLMA"], ["TLMA3"], 0, 0)

    rule_vocab.create_rule("TerminalEndLimb1", ["EM"], ["U1"], 0, 0)
    rule_vocab.create_rule("TerminalEndLimb2", ["EM"], ["U2"], 0, 0)
    rule_vocab.create_rule("TerminalJoint", ["J"], ["J1"], 0, 0)

    list_J = node_vocab.get_list_of_nodes(["J1"])
    list_RM = node_vocab.get_list_of_nodes([
        "TR1", "TR2", "TR3", "TRP1", "TRP2", "TRP3", "TRM1", "TRM2", "TRM3", "TRPA1", "TRPA2",
        "TRPA3", "TRMA1", "TRMA2", "TRMA3"
    ])
    list_LM = node_vocab.get_list_of_nodes([
        "TL1", "TL2", "TL3", "TLP1", "TLP2", "TLP3", "TLM1", "TLM2", "TLM3", "TLPA1", "TLPA2",
        "TLPA3", "TLMA1", "TLMA2", "TLMA3"
    ])
    list_B = node_vocab.get_list_of_nodes(["L1", "L2", "L3", "F1", "F2", "F3", "U1", "U2"])
    # Required for criteria calc
    node_features = [list_B, list_J, list_LM, list_RM]
    return rule_vocab, node_features


def grab_crtitrion(sim_output: dict[int, SimOut], grab_robot, node_feature: list[list[Node]], gait,
                   weight):
    j_nodes = criterion.nodes_division(grab_robot, node_feature[1])
    b_nodes = criterion.nodes_division(grab_robot, node_feature[0])
    rb_nodes = criterion.sort_left_right(grab_robot, node_feature[3], node_feature[0])
    lb_nodes = criterion.sort_left_right(grab_robot, node_feature[2], node_feature[0])

    return criterion.criterion_calc(sim_output, b_nodes, j_nodes, rb_nodes, lb_nodes, weight, gait)


def create_grab_criterion_fun(node_features, gait, weight):

    def fun(sim_output, grab_robot):
        return grab_crtitrion(sim_output, grab_robot, node_features, gait, weight)

    return fun


def create_traj_fun(stop_time: float, time_step: float):

    def fun(graph: GraphGrammar, x: list[float]):
        return create_torque_traj_from_x(graph, x, stop_time, time_step)

    return fun


def create_builder_grasp_object(shape=SimpleBody.BOX,
                                position=FrameTransform([0, 1.5, 0], [0, -0.048, 0.706, 0.706]),
                                material=DefaultChronoMaterial()):

    def builder_grasp_object():

        obj = BlockWrapper(ChronoBodyEnv, shape=shape, material=material, pos=position)

        return obj

    return builder_grasp_object