"""Claw — legs, hook, and sprockets with instancing."""

from tanuki.dsl import *

tolerance = 0.125


def create_claw():
    with model("claw") as ctx:
        c_sprocket = 4.7498

        leg_l = cube(5.5, 50, 2, "base") | place(14.75, 0, 0)
        leg_r = cube(5.5, 50, 2, "base") | place(-14.75, 0, 0)
        top = cube(35, 10, 2, "top") | place(0, 25, 0)

        hook = cylinder(12, 2, "hook") | place(0, 35, 0)
        h_hook = cylinder(8, 2, "h_hook") | place(0, 35, 0)
        h_hook_2 = cube(20, 16, 2, "h_hook_2") | place(10, 30, 0)
        hook = difference(hook, [h_hook, h_hook_2])

        sprocket = cube(
            2.7 - tolerance, 1.9 - tolerance, 3, "sprocket"
        ) | place(0, 0, 1)

        y_positions = [-20 + c_sprocket * i for i in range(9)]
        sprocket_positions = [
            (x, y, 0)
            for y in y_positions
            for x in [28.169 / 2, -28.169 / 2]
        ]

        sprockets = clones(sprocket, sprocket_positions)

        claw = union([leg_l, leg_r, top, hook, sprockets])

        output(claw)
    return ctx.graph


ALL_PARTS = [
    create_claw,
]

if __name__ == "__main__":
    import argparse
    from tanuki.dsl.export import combined_export, individual_export

    parser = argparse.ArgumentParser(description="Compile claw parts")
    parser.add_argument("--mode", choices=["combined", "individual"], default="combined")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    if args.mode == "combined":
        out = args.output or "claw_gen.py"
        path = combined_export(ALL_PARTS, out)
        print(f"Generated {len(ALL_PARTS)} parts in {path} ({path.stat().st_size // 1024} KB)")
    else:
        out = args.output or "claw_gen"
        written = individual_export(ALL_PARTS, out)
        print(f"Generated {len(written)} files in {out}/")
