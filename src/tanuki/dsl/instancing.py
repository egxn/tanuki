"""Instancing operations — pure functions returning IR nodes."""

from __future__ import annotations

from ..ir.nodes import IRInstanceOnPoints, IRNode, Vec3
from .primitives import point
from .operations import join


def clones(node: IRNode, points: list[Vec3]) -> IRInstanceOnPoints:
    """Instance *node* at each position in *points*.

    Creates individual point nodes, joins them, and instances *node* on them.
    """
    point_nodes = tuple(
        point(*p, label=f"{node.label} {i} point")
        for i, p in enumerate(points)
    )
    points_joined = join(list(point_nodes))
    return IRInstanceOnPoints(
        instance=node,
        points=points_joined,
        label=f"{node.label} instance on points" if node.label else "instance on points",
    )
