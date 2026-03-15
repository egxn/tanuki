"""Primitives Showcase — every primitive side by side.

Generates a Blender geometry-nodes script that places each DSL
primitive spaced along the X axis so they are all visible at once.
"""

from tanuki.dsl import (
    model, output, join,
    cube, sphere, cylinder, cone, point, circle, grid, ico_sphere, line,
    translate,
)


def create_primitives_showcase():
    """Build an IR graph with every primitive type, translated along X."""
    with model("primitives_showcase") as ctx:
        spacing = 3.0
        shapes = [
            cube(2, 2, 2, "cube"),
            sphere(1.0, "sphere") | translate(spacing, 0, 0),
            cylinder(0.8, 2.0, "cylinder") | translate(spacing * 2, 0, 0),
            cone(0.0, 1.0, 2.0, "cone") | translate(spacing * 3, 0, 0),
            ico_sphere(1.0, subdivisions=2, label="ico_sphere") | translate(spacing * 4, 0, 0),
            circle(vertices=32, radius=1.0, label="circle") | translate(spacing * 5, 0, 0),
            grid(size_x=2, size_y=2, vertices_x=4, vertices_y=4, label="grid") | translate(spacing * 6, 0, 0),
            line(count=10, start=(0, 0, -1), end=(0, 0, 1), label="line") | translate(spacing * 7, 0, 0),
        ]

        result = join(shapes)
        output(result)

    return ctx.graph


if __name__ == "__main__":
    from tanuki.backends import render

    graph = create_primitives_showcase()
    render(graph, target="blender", mode="script", output_path="primitives_showcase_gen.py")
    print("Generated: primitives_showcase_gen.py")
