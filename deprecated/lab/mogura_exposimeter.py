import sys
sys.path.append("/home/egxn/Catcode/bee/src")

from bee.nodes import *

tolerance = 0.125

def create_container():
    start("container")
    container = cube(26, 26, 36, "container", position=(0, 0, 0))

    h_esp_32 = cube(23 + tolerance * 2 , 2, 36, "ESP32", position=(0, 10, 1.5))
    h_esp_32_2 = cube(20.5, 6, 36, "hole", position=(0, 10, 1.5))
    h_esp_usb = cube(10, 4, 18, "ESP32_USB", position=(0, 12.5, -18))

    h_battery = cube(24 + tolerance * 2, 12, 36, "battery", position=(0, 0, 1.5))
    h_battery_usb = cube(10, 4, 10, "h_battery_usb", position=(-13, 4, 3))
    h_switch = cylinder(2.5, 6, "switch", position=(-13, 3, 13), rotation=(90, 0, 90))

    h_encoder = cube(20 + tolerance * 2, 2, 36, "encoder", position=(0, -10, 1.5))
    h_encoder_2 = cube(18.5, 6, 36, "hole", position=(0, -10, 1.5))

    h_t = cube(12, 24, 36, "t", position=(0, 0, 1.5))

    container = difference(container, [h_encoder, h_esp_32, h_battery, h_esp_32_2, h_encoder_2, h_t, h_esp_usb, h_battery_usb, h_switch])

    output(container)

def create_box():
    start("box")

    box = cube(28, 33, 38, "box", position=(0, -4, 0))
    h_container = cube(26 + tolerance * 2, 31 + tolerance * 2, 38, "container_hole", position=(0, -4, -1))
    h_side_1 = cube(4, 8, 36, "side_hole_1", position=(-12, 1, -1))
    h_side_2 = cube(12, 7, 8, "side_hole_2", position=(0, 14, -1))
    h_side_3 = cube(8, 6, 20, "side_hole_3", position=(-3, -19, -10))
    h_side_4 = cube(12, 12, 20, "side_hole_4", position=(0, 0, 19))

    box = difference(box, [h_container, h_side_1, h_side_2, h_side_3, h_side_4])

    box_1 = cube(4, 1.5, 8, "box_lid", position=(4, 10, 14))
    box_2 = cube(4, 1.5, 8, "box_lid", position=(-4, 10, 14))

    box = union([box, box_1, box_2])

    output(box)

def create_clockwork_knob():
    start("clockwork_knob")

    knob = cylinder(4, 13, "knob_base", position=(0, 0, 0))
    h_knob = cylinder(3 + tolerance, 13, "knob_top", position=(0, 0, -1))

    knob_1 = cylinder(5, 4, "knob_part_1", vertices=10, position=(4, 0, 6), rotation=(0, 90, 90))
    knob_2 = cylinder(5, 4, "knob_part_2", vertices=10, position=(-4, 0, 6), rotation=(0, 90, 90))

    knob = union([knob, knob_1, knob_2])
    knob = difference(knob, [h_knob])

    output(knob)

# create_container()
# create_box()

create_clockwork_knob()