"""Minolta tap — cylindrical tap with lace holder."""

from tanuki.dsl import *

tolerance = 0.125


def create_tap():
    with model("tap") as ctx:
        tap = cylinder(59 / 2, 10, "tap", vertices=128)
        h_tap = cylinder(54.75 / 2, 10, "tap", vertices=128) | place(0, 0, 2)
        h_tap_1 = cylinder(33 / 2, 20, "h_tap_1", vertices=128) | rotate(0, 0, 90)

        tap_0 = difference(tap, [h_tap, h_tap_1])
        line = cube(10, 120, 12, "line")

        tap_1 = intersect([tap_0, line])

        lace_holder = cube(10, 10, 10, "lace_holder")
        h_lace_holder = cylinder(3, 20, "h_lace_holder") | rotate(90, 0, 90)

        lace_holder_1 = difference(lace_holder, [h_lace_holder])

        lace_holder_1 = lace_holder_1 | translate(0, 33, 0)

        tap_1 = union([tap_1, lace_holder_1])

        output(tap_1)
    return ctx.graph


if __name__ == "__main__":
    from tanuki.backends import render

    graph = create_tap()
    render(graph, target="blender", mode="script", output_path="minolta_tap_gen.py")
