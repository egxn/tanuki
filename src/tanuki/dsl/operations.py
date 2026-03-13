"""Boolean and join operations — pure functions returning IR nodes."""

from __future__ import annotations

from ..ir.nodes import BooleanOp, IRBoolean, IRJoin, IRNode


def union(nodes: list[IRNode]) -> IRBoolean:
    """Boolean union of all *nodes*."""
    return IRBoolean(
        operation=BooleanOp.UNION,
        children=tuple(nodes),
        label="union",
    )


def difference(first: IRNode, rest: list[IRNode]) -> IRBoolean:
    """Boolean difference: subtract *rest* from *first*.

    Children tuple: (first, *rest) — first element is the target.
    """
    return IRBoolean(
        operation=BooleanOp.DIFFERENCE,
        children=(first, *rest),
        label="difference",
    )


def intersect(nodes: list[IRNode]) -> IRBoolean:
    """Boolean intersection of all *nodes*."""
    return IRBoolean(
        operation=BooleanOp.INTERSECT,
        children=tuple(nodes),
        label="intersect",
    )


def join(nodes: list[IRNode]) -> IRJoin:
    """Join multiple geometries into one."""
    return IRJoin(
        children=tuple(nodes),
        label="join",
    )
