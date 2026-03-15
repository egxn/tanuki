"""Generate individual primitive examples — one model per primitive.

Each function creates a single-primitive model, compiles it to a bpy script,
and writes it to the examples directory.
"""

from pathlib import Path

from tanuki.dsl import (
    model, output,
    cube, sphere, cylinder, cone, point, circle, grid, ico_sphere, line,
)
from tanuki.backends import render

EXAMPLES_DIR = Path(__file__).parent
GEN_DIR = EXAMPLES_DIR / "gen"


def _gen(name, graph):
    GEN_DIR.mkdir(exist_ok=True)
    out = GEN_DIR / f"{name}_gen.py"
    render(graph, target="blender", mode="script", output_path=str(out))
    print(f"  {out}")


def gen_cube():
    with model("prim_cube") as ctx:
        output(cube(2, 2, 2, "cube"))
    _gen("cube", ctx.graph)


def gen_sphere():
    with model("prim_sphere") as ctx:
        output(sphere(1.0, "sphere", segments=32, rings=16))
    _gen("sphere", ctx.graph)


def gen_cylinder():
    with model("prim_cylinder") as ctx:
        output(cylinder(0.8, 2.5, "cylinder", vertices=32))
    _gen("cylinder", ctx.graph)


def gen_cone():
    with model("prim_cone") as ctx:
        output(cone(0.0, 1.0, 2.0, "cone"))
    _gen("cone", ctx.graph)


def gen_ico_sphere():
    with model("prim_ico_sphere") as ctx:
        output(ico_sphere(1.0, subdivisions=2, label="ico_sphere"))
    _gen("ico_sphere", ctx.graph)


def gen_circle():
    with model("prim_circle") as ctx:
        output(circle(vertices=32, radius=1.0, fill_type="NGON", label="circle"))
    _gen("circle", ctx.graph)


def gen_grid():
    with model("prim_grid") as ctx:
        output(grid(size_x=2, size_y=2, vertices_x=6, vertices_y=6, label="grid"))
    _gen("grid", ctx.graph)


def gen_line():
    with model("prim_line") as ctx:
        output(line(count=10, start=(0, 0, -1), end=(0, 0, 1), label="line"))
    _gen("line", ctx.graph)


ALL = [gen_cube, gen_sphere, gen_cylinder, gen_cone, gen_ico_sphere, gen_circle, gen_grid, gen_line]

if __name__ == "__main__":
    print("Generating individual primitive scripts:")
    for fn in ALL:
        fn()
    print("Done.")
