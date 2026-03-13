
import sys
sys.path.append("/home/egxn/Catcode/bee/src")

from bee.nodes import *

tolerance = 0.125


def create_base_board():
    start("base_board")
    base_board = cube(350, 350, 2, "base_board", position=(0, 0, -3/2))
    output(base_board)

def create_container_step_motor(start_name =  "container_step_motor"):
    start(start_name)

    container = cylinder(16, 16, "container")
    h_container = cylinder(14 + tolerance, 16, "h_container")
    base_container = cylinder(16, 2, "base_container", position=(0, 0, -9))
    
    col_1 = cylinder(5, 18, "col_1", position=(35/2, 0, -1))
    col_2 = cylinder(5, 18, "col_2", position=(-35/2, 0, -1))
    col_screw_1 = cylinder(2 - tolerance, 18, "col_screw_1", position=(35/2, 0, 2))
    col_screw_2 = cylinder(2 - tolerance, 18, "col_screw_2", position=(-35/2, 0, 2))

    wires = cube(20, 14, 16, "wires", position=(0, -16, 0))
    base_wires = cube(20, 14, 2, "base_wires", position=(0, -16, -9))
    h_wires = cube(17 + tolerance * 2, 10, 16, "h_wires", position=(0, -16, 0))
    # h_wires_2 = cylinder(4 + tolerance, 16, "h_wires_2", position=(0, -16, 8), rotation=(90, 0, 0))

    container = union([base_container, container, col_1, col_2, col_screw_1, col_screw_2, wires, base_wires])

    step_motor = difference(container, [h_container, h_wires])

    if start_name != "container_step_motor":
        return step_motor
    else:
        screw_base = cube(6, 53, 2, "screw_base", position=(0, -3.5, -9))
        h_screw_1 = cylinder(2 + tolerance, 2, "h_screw_1", position=(0, 19, -9), rotation=(0, 0, 0))
        h_screw_2 = cylinder(2 + tolerance, 2, "h_screw_2", position=(0, -26, -9), rotation=(0, 0, 0))
        screw_base = difference(screw_base, [h_screw_1, h_screw_2])

        step_motor = union([step_motor, screw_base])
        output(step_motor)

def create_stepper_motor(start_name = "stepper_motor"):
    start(start_name)

    container = cylinder(14, 19.3, "container", position=(0, 0, 0))
    axis_1 = cylinder(9.2/2, 21, "axis_1", position=(0, 8, 1.7))

    axis_2 = cylinder(2.5, 29, "axis_2", position=(0, 8, 5))
    axis_3 = cube(6, 3, 29, "axis_3", position=(0, 8, 5))
    axis_2 = intersect([axis_2, axis_3])

    screw_supp_1 = cube(35, 6.9, 0.5, "screw_supp", position=(0, 0, 8))
    screw_supp_2 = cylinder(3.5, 0.5, "screw_supp", position=(35/2, 0, 8))
    screw_supp_3 = cylinder(3.5, 0.5, "screw_supp", position=(-35/2, 0, 8))
    screw_supp = union([screw_supp_1, screw_supp_2, screw_supp_3])
    h_screw_supp_2 = cylinder(2, 0.5, "screw_supp", position=(35/2, 0, 8))
    h_screw_supp_3 = cylinder(2, 0.5, "screw_supp", position=(-35/2, 0, 8))

    screw_supp = difference(screw_supp, [h_screw_supp_2, h_screw_supp_3])

    step_motor = union([container, axis_1, axis_2, screw_supp])

    t_step_motor = transform(step_motor, translation=(0, 0, 1.65))

    if start_name != "stepper_motor":
        return step_motor
    else:
        output(t_step_motor)

def create_arm_connection(start_name = "arm_connection"):
    start(start_name)

    joint = cylinder(9.2/2, 10, "joint", position=(0, 0, 0))

    axis_2 = cylinder(2.5 + tolerance, 6, "axis_2", position=(0, 0, -2))
    axis_3 = cube(6, 3, 6, "axis_3", position=(0, 0, -2))
    h_axis_2 = intersect([axis_2, axis_3])
    h_axis_2 = transform(h_axis_2, rotation=(0, 0, 90))

    base = cylinder(6, 2, "base", position=(0, 0, 4))

    h_arm = cylinder(4.5 + tolerance, 12, "h_arm", position=(8, 0, 0), rotation=(0, 90, 0))

    arm_1 = cube(14, 12, 10, "arm_1", position=(6, 0, 0))

    joint = union([joint, base, arm_1])
    joint = difference(joint, [h_axis_2, h_arm])

    t_joint = transform(joint, translation=(0, 8, 20.5), rotation=(0, 0, 90))

    if start_name != "arm_connection":
        return joint
    else:
        output(t_joint)

def create_motor_2():
    motor = create_stepper_motor("motor_2")
    t_motor = transform(motor, translation=(0, 152, 20), rotation=(0, 180, 0))
    output(t_motor)

def create_container_step_motor_2():
    container = create_container_step_motor("container_step_motor_2")

    wires = cube(20, 14, 18, "wires", position=(0, -28, -1))
    h_arm = cylinder(4.5 + tolerance, 14, "h_arm", position=(0, -30, 1.75), rotation=(90, 180, 0))

    container = union([container, wires])
    container = difference(container, [h_arm])

    t_container = transform(container, translation=(0, 152, 22), rotation=(0, 180, 0))
    output(t_container)

def create_arm_connection_2():
    arm = create_arm_connection("arm_connection_2")
    t_arm = transform(arm, translation=(0, 160, 0), rotation=(180, 0, 90))
    output(t_arm)

def create_arm_connection_3(start_name = "arm_connection_3"):
    start(start_name)
    block = cube(20, 12, 10, "block", position=(0, 0, 0))
    h_arm_1 = cylinder(4.5 + tolerance, 10, "h_arm_1", position=(7, 0, 0), rotation=(0, 90, 0))
    h_arm_2 = cylinder(4.5 + tolerance, 10, "h_arm_2", position=(-4, 0, 2))

    block = difference(block, [h_arm_1, h_arm_2])

    if start_name != "arm_connection_3":
        return block
    else:
        t_block = transform(block, translation=(0, 310, 0), rotation=(0, 0, 270))
        output(t_block)

def create_arm_connection_4():
    arm = create_arm_connection_3("arm_connection_4")
    t_arm = transform(arm, translation=(0, 310, 20), rotation=(0, 180, 0))
    output(t_arm)

create_container_step_motor()
create_stepper_motor()
create_arm_connection()

create_motor_2()
create_container_step_motor_2()
create_arm_connection_2()
create_arm_connection_3()
create_arm_connection_4()
