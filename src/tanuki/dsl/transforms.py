"""Transform operations — composable via the ``|`` pipe operator.

Two styles are supported:

1. **Curried** (preferred for composition)::

       cube(10, 10, 10) | place(5, 0, 0) | rotate(0, 0, 45)

2. **Direct** (when you already hold a reference)::

       transform(node, translation=(1, 2, 3), rotation=(90, 0, 0))

Each curried function returns a ``Callable[[IRNode], IRNode]`` that can be
combined with the ``|`` operator on any IRNode, or passed to :func:`pipe`.
"""

from __future__ import annotations

from collections.abc import Callable

from ..ir.nodes import IRNode, IRSetPosition, IRTransform, Vec3

# Type alias — any function that transforms a node is an Op.
Op = Callable[[IRNode], IRNode]


# ---------------------------------------------------------------------------
# Curried transforms (return Op)
# ---------------------------------------------------------------------------


def translate(x: float = 0, y: float = 0, z: float = 0) -> Op:
    """Return an op that wraps a node in an ``IRTransform`` with translation."""
    def _apply(node: IRNode) -> IRTransform:
        return IRTransform(
            child=node,
            translation=(x, y, z),
            label=f"{node.label} translate" if node.label else "translate",
        )
    return _apply


def rotate(rx: float = 0, ry: float = 0, rz: float = 0) -> Op:
    """Return an op that wraps a node in an ``IRTransform`` with rotation (degrees)."""
    def _apply(node: IRNode) -> IRTransform:
        return IRTransform(
            child=node,
            rotation=(rx, ry, rz),
            label=f"{node.label} rotate" if node.label else "rotate",
        )
    return _apply


def scale_by(sx: float = 1, sy: float = 1, sz: float = 1) -> Op:
    """Return an op that wraps a node in an ``IRTransform`` with scale."""
    def _apply(node: IRNode) -> IRTransform:
        return IRTransform(
            child=node,
            scale=(sx, sy, sz),
            label=f"{node.label} scale" if node.label else "scale",
        )
    return _apply


def place(x: float = 0, y: float = 0, z: float = 0) -> Op:
    """Return an op that wraps a node in an ``IRSetPosition`` offset."""
    def _apply(node: IRNode) -> IRSetPosition:
        return IRSetPosition(
            child=node,
            offset=(x, y, z),
            label=f"{node.label} position" if node.label else "position",
        )
    return _apply


# ---------------------------------------------------------------------------
# Direct transforms (take a node, return a node)
# ---------------------------------------------------------------------------


def transform(
    node: IRNode,
    translation: Vec3 | None = None,
    rotation: Vec3 | None = None,
    scale: Vec3 | None = None,
) -> IRTransform:
    """Wrap *node* in a single ``IRTransform`` with any combination of
    translation / rotation / scale.

    Rotation values are in **degrees** — the backend converts to radians.
    """
    return IRTransform(
        child=node,
        translation=translation,
        rotation=rotation,
        scale=scale,
        label=f"{node.label} transform" if node.label else "transform",
    )


def set_position(node: IRNode, position: Vec3) -> IRSetPosition:
    """Set an absolute position offset on *node*."""
    return IRSetPosition(
        child=node,
        offset=position,
        label=f"{node.label} position" if node.label else "position",
    )


# ---------------------------------------------------------------------------
# Composition utility
# ---------------------------------------------------------------------------


def pipe(node: IRNode, *ops: Op) -> IRNode:
    """Apply a sequence of operations to *node* left-to-right.

    Equivalent to ``node | op1 | op2 | …`` but useful when ops are in a list::

        pipe(cube(10, 10, 10), place(5, 0, 0), rotate(0, 0, 45))
    """
    result = node
    for op in ops:
        result = op(result)
    return result
