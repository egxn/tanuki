"""Intermediate Representation for geometry operations."""

from .nodes import (
    IRNode,
    IRPrimitive,
    IRBoolean,
    IRTransform,
    IRSetPosition,
    IRJoin,
    IRInstanceOnPoints,
    IROutput,
    IRValue,
    IRVector,
    PrimitiveType,
    BooleanOp,
    Vec3,
)
from .graph import IRGraph, add_node, set_root, to_dict
