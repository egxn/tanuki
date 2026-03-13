import sys
sys.path.append("/home/egxn/Catcode/bee/src")

from bee.nodes import *

tolerance = 0.125


def create_tray():
    start("tray")
    

    base = cube(107.5, 31, 9, "base", position=(0, 0, 0))

    h_base_1 = cube(103, 31, 9, "h_base_1", position=(0, -2, 2))
    h_base_2 = cube(23, 31, 9, "h_base_2", position=(0, 0, 2))
    h_base_3 = cube(12, 31, 9, "h_base_3", position=(25, 0, 2))
    h_base_4 = cube(12, 31, 9, "h_base_4", position=(-25, 0, 2))
    h_base_5 = cube(3, 31, 2, "h_base_5", position=(36.5, 0, -4.5))
    h_base_6 = cube(3, 31, 2, "h_base_6", position=(-36.5, 0, -4.5))

    base = difference(
        base, [
            h_base_1,
            h_base_2,
            h_base_3,
            h_base_4,
            h_base_5,
            h_base_6,
        ]
    )

    output(base)


create_tray()
