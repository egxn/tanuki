"""Attribute operations — store named attribute, remove named attribute."""

from __future__ import annotations

from collections.abc import Callable

from ..ir.nodes import IRGeometryOp, IRNode

Op = Callable[[IRNode], IRNode]


def store_named_attribute(
    name: str = "",
    value: float | IRNode = 0.0,
    data_type: str = "FLOAT",
    domain: str = "POINT",
) -> Op:
    """Store a value into a named attribute on geometry elements."""
    def _apply(node: IRNode) -> IRGeometryOp:
        extra: dict[str, IRNode] = {}
        props: dict[str, object] = {
            "name": name,
            "data_type": data_type,
            "domain": domain,
        }
        if isinstance(value, IRNode):
            extra["Value"] = value
        else:
            props["value"] = value
        return IRGeometryOp(
            op_type="GeometryNodeStoreNamedAttribute",
            child=node,
            properties=props,
            extra_children=extra,
            label=f"{node.label} store_attr" if node.label else "store_named_attribute",
        )
    return _apply


def remove_named_attribute(name: str = "") -> Op:
    """Remove a named attribute from geometry."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeRemoveAttribute",
            child=node,
            properties={"name": name},
            label=f"{node.label} rm_attr" if node.label else "remove_named_attribute",
        )
    return _apply
