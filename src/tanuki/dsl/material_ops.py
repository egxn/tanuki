"""Material operations — set material, replace material, set material index."""

from __future__ import annotations

from collections.abc import Callable

from ..ir.nodes import IRGeometryOp, IRNode

Op = Callable[[IRNode], IRNode]


def set_material(material: str = "") -> Op:
    """Assign a material to geometry elements by name."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSetMaterial",
            child=node,
            properties={"material": material},
            label=f"{node.label} set_mat" if node.label else "set_material",
        )
    return _apply


def replace_material(old: str = "", new: str = "") -> Op:
    """Swap one material with another by name."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeReplaceMaterial",
            child=node,
            properties={"material_old": old, "material_new": new},
            label=f"{node.label} replace_mat" if node.label else "replace_material",
        )
    return _apply


def set_material_index(material_index: int = 0) -> Op:
    """Set the material index for each selected geometry element."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSetMaterialIndex",
            child=node,
            properties={"material_index": material_index},
            label=f"{node.label} set_mat_idx" if node.label else "set_material_index",
        )
    return _apply
