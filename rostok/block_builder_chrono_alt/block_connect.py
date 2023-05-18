import pychrono.core as chrono
import pychrono.irrlicht as chronoirr

from rostok.block_builder_api.easy_body_shapes import Box
from rostok.block_builder_chrono_alt.block_classes import (BLOCK_CLASS_TYPES,
                                                       BuildingBody,
                                                       ChronoRevolveJoint,
                                                       ChronoTransform,
                                                       PrimitiveBody)
from rostok.block_builder_chrono_alt.block_types import (Block, BlockBody,
                                                     BlockBridge,
                                                     BlockTransform, BlockType)
from rostok.block_builder_chrono_alt.blocks_utils import FrameTransform


def place_next_block(prev_block: BuildingBody, next_block: BuildingBody, system: chrono.ChSystem):
    system.Update()
    # prev_body is already added to the system
    next_body: chrono.ChBody = next_block.body
    total_transformation = prev_block.transformed_frame_out.GetAbsCoord() * chrono.ChFrameD(
        next_block.transformed_frame_input).GetInverse().GetCoord()
    # print(prev_block.transformed_frame_out.GetAbsCoord().pos,
    #       prev_block.transformed_frame_out.GetAbsCoord().rot)
    # print(chrono.ChFrameD(next_block.transformed_frame_input).GetInverse().GetCoord().pos)
    # print(total_transformation.pos, total_transformation.rot)
    # print()
    next_body.SetCoord(total_transformation)
    system.Add(next_body)
    system.Update()


def make_fix_joint(prev_block: BuildingBody, next_block: BuildingBody, system: chrono.ChSystem):
    system.Update()
    prev_body = prev_block.body
    next_body = next_block.body

    fix_joint = chrono.ChLinkMateFix()
    fix_joint.Initialize(prev_body, next_body, True, prev_block.transformed_frame_out,
                         next_block.transformed_frame_input)
    system.Add(fix_joint)
    system.Update()

# the function places and connects a sequence of blocks. The sequence should start from the root block
def place_and_connect(sequence: list[BLOCK_CLASS_TYPES], system: chrono.ChSystem):
    # all connections occurs between bodies
    previous_body_block = sequence[0]
    if not previous_body_block.is_build:
        system.AddBody(previous_body_block.body)
        system.Update()

    previous_joint = None
    for it, block in enumerate(sequence):
        if it == 0: continue

        if block.block_type is BlockType.BODY:
            if not block.is_build:
                # check for the input transforms
                if sequence[it - 1].block_type is BlockType.TRANSFORM_INPUT:
                    i = 1
                    transform = True
                    while transform:
                        i += 1
                        if not (sequence[it - i].block_type is BlockType.TRANSFORM_INPUT):
                            transform = False
                            current_transform = chrono.ChCoordsysD()
                            for k in range(it - i + 1, it):
                                current_transform = current_transform * sequence[k].transform
                            block.apply_input_transform(current_transform)
                        else:
                            continue
                # if there is no previous joint the body connects to the previous bodywith fix joint
                if previous_joint is None:
                        place_next_block(previous_body_block, block, system)
                        make_fix_joint(previous_body_block, block, system)
                # if there is a joint the body connects to it with a fix joint
                else:
                    place_next_block(previous_joint, block, system)
                    make_fix_joint(previous_joint, block, system)
                    previous_joint = None
            else:
                previous_joint = None
            previous_body_block = block

            block.is_build = True
        
        # transforms follow the block and shift the outer transformed frame,
        # using inner function `apply_transform`
        elif block.block_type is BlockType.TRANSFORM_OUT:
            i = 0
            transform = True
            while transform:
                i += 1
                if sequence[it - i].block_type is BlockType.BODY:
                    transform = False
                    current_transform = chrono.ChCoordsysD()
                    for k in range(it - i + 1, it + 1):
                        current_transform = current_transform * sequence[k].transform

                    sequence[it - i].apply_transform_out(current_transform)

                elif sequence[it - i].block_type is BlockType.BRIDGE:
                    transform = False
                    current_transform = chrono.ChCoordsysD()
                    for k in range(it - i + 1, it + 1):
                        current_transform = current_transform * sequence[k].transform

                    sequence[it - i].apply_cental_transform(current_transform)
                else:
                    continue
        # self transformations follows are applied to the next body input frame
        elif block.block_type is BlockType.TRANSFORM_INPUT:
            continue

        if block.block_type is BlockType.BRIDGE:
            
            if previous_joint is None:
                # it pulls the prev body transformed frame in its y direction for the radius of the joint
                block.set_prev_body_frame(previous_body_block, system)
                place_next_block(previous_body_block, block, system)
            else:
                place_next_block(previous_joint, block, system)
                previous_joint.connect(block, system)

            previous_joint = block

if __name__ == "__main__":
    chrono_system = chrono.ChSystemNSC()
    chrono_system.SetSolverType(chrono.ChSolver.Type_BARZILAIBORWEIN)
    chrono_system.SetSolverMaxIterations(100)
    chrono_system.SetSolverForceTolerance(1e-6)
    chrono_system.SetTimestepperType(chrono.ChTimestepper.Type_EULER_IMPLICIT_LINEARIZED)
    chrono_system.Set_G_acc(chrono.ChVectorD(0, 0, 0))
    flat = PrimitiveBody(shape=Box(0.25, 0.05, 0.8))
    x = 0.35
    transform = ChronoTransform(FrameTransform([-x, 0, 0], [1, 0, 0, 0]))
    joint = ChronoRevolveJoint(starting_angle=0)

    link = PrimitiveBody(shape=Box(0.1, 0.6, 0.4))
    mount = PrimitiveBody(shape=Box(0.1, 0.05, 0.4))

    block_list = [flat, transform, joint, link, mount]

    place_and_connect(block_list, chrono_system)
    flat.body.SetBodyFixed(True)
    joint.joint.SetTorqueFunction(chrono.ChFunction_Const(1))
    x = 0.5
    transform2 = transform = ChronoTransform(FrameTransform([x, 0, +0.3], [1, 0, 0, 0]))
    mount2 = PrimitiveBody(shape=Box(0.2, 0.05, 0.4))
    block_list = [flat, transform2, mount2]
    place_and_connect(block_list, chrono_system)
    transform2 = transform = ChronoTransform(FrameTransform([x, 0, -0.3], [1, 0, 0, 0]))
    mount2 = PrimitiveBody(shape=Box(0.2, 0.05, 0.4))
    block_list = [flat, transform2, mount2]
    place_and_connect(block_list, chrono_system)
    # coord_flat = flat.transformed_frame_out.GetCoord()
    # coord_link = link.transformed_frame_input.GetCoord()
    # coord_link_abs = link.transformed_frame_input.GetAbsCoord()

    # print(coord_flat.pos, coord_flat.rot)
    # print(coord_link.pos, coord_link.rot)
    # print(coord_link_abs.pos, coord_link_abs.rot)

    vis = chronoirr.ChVisualSystemIrrlicht()
    vis.AttachSystem(chrono_system)
    vis.SetWindowSize(1024, 768)
    vis.SetWindowTitle('Grab demo')
    vis.Initialize()
    vis.AddCamera(chrono.ChVectorD(1.5, 3, -2))
    vis.AddTypicalLights()
    vis.EnableCollisionShapeDrawing(True)

    # Simulation loop
    while vis.Run():
        chrono_system.Update()
        chrono_system.DoStepDynamics(5e-3)
        vis.BeginScene(True, True, chrono.ChColor(0.2, 0.2, 0.3))
        vis.Render()
        vis.EndScene()
    # place_and_connect(body_list)