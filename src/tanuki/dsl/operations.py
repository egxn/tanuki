"""Boolean and join operations — pure functions returning IR nodes."""

from __future__ import annotations

from ..ir.nodes import BooleanOp, IRBoolean, IRJoin, IRNode


def union(nodes: list[IRNode], solver: str = "EXACT") -> IRBoolean:
    """Boolean union of all *nodes*.

    *solver* selects the Mesh Boolean solver: ``"EXACT"`` (default),
    ``"FLOAT"`` (fast/tolerant) or ``"MANIFOLD"`` (fast and clean for
    manifold inputs — good for fusing many overlapping solids).
    """
    return IRBoolean(
        operation=BooleanOp.UNION,
        children=tuple(nodes),
        label="union",
        solver=solver,
    )


def difference(first: IRNode, rest: list[IRNode], solver: str = "EXACT") -> IRBoolean:
    """Boolean difference: subtract *rest* from *first*.

    Children tuple: (first, *rest) — first element is the target.
    See :func:`union` for *solver*.
    """
    return IRBoolean(
        operation=BooleanOp.DIFFERENCE,
        children=(first, *rest),
        label="difference",
        solver=solver,
    )


def intersect(nodes: list[IRNode], solver: str = "EXACT") -> IRBoolean:
    """Boolean intersection of all *nodes*.  See :func:`union` for *solver*."""
    return IRBoolean(
        operation=BooleanOp.INTERSECT,
        children=tuple(nodes),
        label="intersect",
        solver=solver,
    )


def join(nodes: list[IRNode]) -> IRJoin:
    """Join multiple geometries into one."""
    return IRJoin(
        children=tuple(nodes),
        label="join",
    )
