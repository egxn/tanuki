from tanuki.dsl import *

tolerance = 0.125

def create_bls_50_battery():
    with model("bls_50_battery") as ctx:
        base = cube(35, 12, 55, "bls_50_base")
        h_base = cube(31, 11, 50, "bls_50_hole_base")
        h_base_1 = cube(31, 8, 50, "bls_50_hole_base_1") | place(0, 0, -1)
        h_base_2 = cube(24, 8, 48, "bls_50_hole_base_2") | place(0, -2, 0)
        h_base_3 = cube(24, 8, 48, "bls_50_hole_base_3") | place(0, 0, -55/2)
        h_pad_base = cylinder(2.75, 10, "bls_50_hole1") | place(0, 0, -1)
        h_pads_base = clones(h_pad_base, [
            (3.4, 2.7, 55/2),
            (-9.8, 2.7, 55/2),
        ])
        h_keying_slot = cube(4, 4, 10, "bls_50_hole_keying_slot") | place(-15.6, 5.3, 55/2) 

        pad = cube(8, 6, 10, "bls_50_pad")
        h_pads = clones(pad, [
            (3.4, 2.7, 55/2 - 7),
            (-9.8, 2.7, 55/2 - 7),
        ])

        base = difference(base, [
            h_base,
            h_base_1,
            h_base_2,
            h_base_3,
            h_keying_slot,
        ])

        base = union([
            base,
            h_pads,
        ])

        h_pad = cylinder(2 + tolerance, 3 + tolerance, "bls_50_hole_pad")
        h_pad_1 = cylinder(1.5 + tolerance, 15, "bls_50_hole_pad_1", 8) | rotate(0, 0, 22.5)

        base = difference(base, [
            h_pad | place(3.4, 2.7, 55/2 - 3.25),
            h_pad | place(-9.8, 2.7, 55/2 - 3.25),
            h_pad_1 | place(3.4, 2.7, 55/2 - 7),
            h_pad_1 | place(-9.8, 2.7, 55/2 - 7),
            h_pads_base,
        ])

        output(base)
    return ctx.graph


if __name__ == "__main__":
    from tanuki.backends import render

    graph = create_bls_50_battery()
    render(graph, target="blender", mode="script", output_path="bls_50_battery_gen.py")
