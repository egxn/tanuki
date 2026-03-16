"""Frozen dataclass definitions for the Intermediate Representation (IR).

All IR nodes are immutable. Transformations produce new nodes.
Collections use tuples (not lists) to enforce immutability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Union
from uuid import uuid4


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

Vec3 = tuple[float, float, float]


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class PrimitiveType(Enum):
    CUBE = auto()
    SPHERE = auto()
    CYLINDER = auto()
    CONE = auto()
    POINT = auto()
    # Mesh primitives
    CIRCLE = auto()
    GRID = auto()
    ICO_SPHERE = auto()
    LINE = auto()
    # Curve primitives
    CURVE_ARC = auto()
    CURVE_CIRCLE = auto()
    CURVE_LINE = auto()
    CURVE_QUADRILATERAL = auto()
    CURVE_STAR = auto()
    CURVE_SPIRAL = auto()
    CURVE_BEZIER_SEGMENT = auto()
    CURVE_QUADRATIC_BEZIER = auto()
    # Volume primitives
    VOLUME_CUBE = auto()
    # Importers
    IMPORT_OBJ = auto()
    IMPORT_STL = auto()
    IMPORT_PLY = auto()
    IMPORT_CSV = auto()
    IMPORT_VDB = auto()
    # Reference sources
    COLLECTION_INFO = auto()
    OBJECT_INFO = auto()


class BooleanOp(Enum):
    UNION = auto()
    DIFFERENCE = auto()
    INTERSECT = auto()


# ---------------------------------------------------------------------------
# Helper: auto-generate a unique id per node
# ---------------------------------------------------------------------------


def _new_id() -> str:
    return uuid4().hex[:8]


# ---------------------------------------------------------------------------
# IR Nodes  (all frozen)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IRNode:
    """Base class for all IR nodes.

    Supports the pipe operator ``|`` for functional composition::

        cube(10, 10, 10) | place(5, 0, 0) | rotate(0, 0, 45)

    Any ``Callable[[IRNode], IRNode]`` can be used on the right-hand side.
    """

    id: str = field(default_factory=_new_id)
    label: str = ""

    def __or__(self, op):
        """Pipe operator: ``node | op`` calls ``op(node)``."""
        if callable(op):
            return op(self)
        return NotImplemented


@dataclass(frozen=True)
class IRValue(IRNode):
    """Scalar float value node."""

    value: float = 0.0


@dataclass(frozen=True)
class IRVector(IRNode):
    """3-component vector node."""

    value: Vec3 = (0.0, 0.0, 0.0)


@dataclass(frozen=True)
class IRPrimitive(IRNode):
    """Geometry primitive (cube, sphere, cylinder, cone, point)."""

    primitive_type: PrimitiveType = PrimitiveType.CUBE
    properties: dict[str, Union[float, int, Vec3]] = field(default_factory=dict)


@dataclass(frozen=True)
class IRBoolean(IRNode):
    """Boolean operation on geometry (union, difference, intersect)."""

    operation: BooleanOp = BooleanOp.UNION
    # For DIFFERENCE: first element is the target, rest are operands.
    # For UNION/INTERSECT: all elements are equal operands.
    children: tuple[IRNode, ...] = ()


@dataclass(frozen=True)
class IRTransform(IRNode):
    """Apply translation/rotation/scale to child geometry."""

    child: IRNode | None = None
    translation: Vec3 | None = None
    rotation: Vec3 | None = None  # degrees — backend converts to radians
    scale: Vec3 | None = None


@dataclass(frozen=True)
class IRSetPosition(IRNode):
    """Set absolute position offset on child geometry."""

    child: IRNode | None = None
    offset: Vec3 = (0.0, 0.0, 0.0)


@dataclass(frozen=True)
class IRJoin(IRNode):
    """Join multiple geometries into one."""

    children: tuple[IRNode, ...] = ()


@dataclass(frozen=True)
class IRInstanceOnPoints(IRNode):
    """Instance geometry on a set of points."""

    instance: IRNode | None = None
    points: IRNode | None = None


@dataclass(frozen=True)
class IRGeometryOp(IRNode):
    """Single-child geometry operation (extrude, subdivide, etc.).

    ``extra_children`` holds additional named geometry inputs, e.g.
    ``{"Profile Curve": <IRNode>}`` for *Curve to Mesh*.
    """

    op_type: str = ""
    child: IRNode | None = None
    properties: dict[str, object] = field(default_factory=dict)
    extra_children: dict[str, IRNode] = field(default_factory=dict)


@dataclass(frozen=True)
class IRSeparateComponents(IRNode):
    """Separate geometry into mesh, curves, points, etc."""

    child: IRNode | None = None
    component: str = "Mesh"


@dataclass(frozen=True)
class IRFieldInput(IRNode):
    """Field input node (Position, Normal, Index, Edge Angle, etc.).

    These nodes have no geometry input — they produce field values
    evaluated per-element in the context where they are used.

    ``field_type`` is the Blender node type string, e.g.
    ``"GeometryNodeInputPosition"``.
    ``output_socket`` selects which output to use (default first).
    """

    field_type: str = ""
    output_socket: str = ""
    properties: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class IRMathOp(IRNode):
    """Scalar or vector math operation.

    ``math_type`` is the Blender node type (``"ShaderNodeMath"`` or
    ``"ShaderNodeVectorMath"``).
    ``operation`` is the Blender enum string (``"ADD"``, ``"SUBTRACT"``,
    ``"MULTIPLY"``, ``"NORMALIZE"``, etc.).
    ``inputs`` maps socket names/indices to IR nodes that provide the values.
    ``clamp`` enables output clamping (scalar math only).
    """

    math_type: str = ""                     # "ShaderNodeMath" | "ShaderNodeVectorMath"
    operation: str = "ADD"
    inputs: dict[str, IRNode] = field(default_factory=dict)
    clamp: bool = False


@dataclass(frozen=True)
class IROutput(IRNode):
    """Root output node of the graph."""

    child: IRNode | None = None
