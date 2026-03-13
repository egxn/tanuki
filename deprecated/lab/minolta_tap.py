import sys
sys.path.append("/home/egxn/Catcode/bee/src")

from bee.nodes import *

tolerance = 0.125

def create_tap():
    start("tap")

    tap = cylinder(59/2, 10, "tap", vertices=128)
    h_tap = cylinder(54.75/2, 10, "tap", vertices=128, position=(0, 0, 2))
    h_tap_1 = cylinder(33/2, 20, "h_tap_1", vertices=128, rotation=(0, 0, 90))

    tap_0 = difference(tap, [h_tap, h_tap_1])
    line = cube(10, 120, 12, "line")

    tap_1 = intersect([tap_0, line])


    lace_holder = cube(10, 10, 10, "lace_holder")
    h_lace_holder = cylinder(3, 20, "h_lace_holder", rotation=(90, 0, 90))

    lace_holder_1 = difference(lace_holder, [h_lace_holder])

    lace_holder_1 = transform(lace_holder_1, translation=(0, 33, 0))

    tap_1 = union([tap_1, lace_holder_1])

    output(tap_1)


create_tap()
