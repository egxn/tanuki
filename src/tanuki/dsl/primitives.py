"""Primitive geometry constructors — pure functions returning IRPrimitive.

Each function creates **only** the geometry node.  Transforms (translate,
rotate, scale, place) are applied separately via the ``|`` pipe operator::

    cube(10, 20, 5, "base") | place(5, 0, 0) | rotate(0, 0, 45)
"""

from __future__ import annotations

from ..ir.nodes import IRPrimitive, PrimitiveType


def cube(x: float, y: float, z: float, label: str = "") -> IRPrimitive:
    """Create a cube primitive with size (*x*, *y*, *z*)."""
    return IRPrimitive(
        primitive_type=PrimitiveType.CUBE,
        label=label,
        properties={"size": (x, y, z)},
    )


def sphere(
    r: float,
    label: str = "",
    segments: int | None = None,
    rings: int | None = None,
) -> IRPrimitive:
    """Create a UV sphere primitive with radius *r*."""
    props: dict = {"radius": r}
    if segments is not None:
        props["segments"] = segments
    if rings is not None:
        props["rings"] = rings
    return IRPrimitive(
        primitive_type=PrimitiveType.SPHERE,
        label=label,
        properties=props,
    )


def cylinder(
    r: float,
    d: float,
    label: str = "",
    vertices: int = 32,
) -> IRPrimitive:
    """Create a cylinder primitive with radius *r* and depth *d*."""
    return IRPrimitive(
        primitive_type=PrimitiveType.CYLINDER,
        label=label,
        properties={"radius": r, "depth": d, "vertices": vertices},
    )


def cone(
    r1: float,
    r2: float,
    d: float,
    label: str = "",
) -> IRPrimitive:
    """Create a cone primitive with radii (*r1*, *r2*) and depth *d*."""
    return IRPrimitive(
        primitive_type=PrimitiveType.CONE,
        label=label,
        properties={"radius_top": r1, "radius_bottom": r2, "depth": d},
    )


def point(x: float = 0, y: float = 0, z: float = 0, label: str = "") -> IRPrimitive:
    """Create a single point at (*x*, *y*, *z*)."""
    return IRPrimitive(
        primitive_type=PrimitiveType.POINT,
        label=label,
        properties={"position": (x, y, z)},
    )


def circle(
    vertices: int = 32,
    radius: float = 1.0,
    fill_type: str = "NONE",
    label: str = "",
) -> IRPrimitive:
    """Create a mesh circle."""
    return IRPrimitive(
        primitive_type=PrimitiveType.CIRCLE,
        label=label,
        properties={"vertices": vertices, "radius": radius, "fill_type": fill_type},
    )


def grid(
    size_x: float = 1.0,
    size_y: float = 1.0,
    vertices_x: int = 3,
    vertices_y: int = 3,
    label: str = "",
) -> IRPrimitive:
    """Create a mesh grid."""
    return IRPrimitive(
        primitive_type=PrimitiveType.GRID,
        label=label,
        properties={
            "size_x": size_x, "size_y": size_y,
            "vertices_x": vertices_x, "vertices_y": vertices_y,
        },
    )


def ico_sphere(
    radius: float = 1.0,
    subdivisions: int = 2,
    label: str = "",
) -> IRPrimitive:
    """Create an icosphere primitive."""
    return IRPrimitive(
        primitive_type=PrimitiveType.ICO_SPHERE,
        label=label,
        properties={"radius": radius, "subdivisions": subdivisions},
    )


def line(
    count: int = 10,
    start: tuple[float, float, float] = (0, 0, 0),
    end: tuple[float, float, float] = (0, 0, 1),
    label: str = "",
) -> IRPrimitive:
    """Create a mesh line."""
    return IRPrimitive(
        primitive_type=PrimitiveType.LINE,
        label=label,
        properties={"count": count, "start_location": start, "end_location": end},
    )
