"""Instance operations — realize, rotate, scale, translate."""

from __future__ import annotations

from collections.abc import Callable

from ..ir.nodes import IRGeometryOp, IRNode

Op = Callable[[IRNode], IRNode]


def realize_instances() -> Op:
    """Realize instances into real geometry."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeRealizeInstances",
            child=node,
            label=f"{node.label} realize" if node.label else "realize",
        )
    return _apply


def rotate_instances(rx: float = 0, ry: float = 0, rz: float = 0) -> Op:
    """Rotate instances in-place (degrees)."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeRotateInstances",
            child=node,
            properties={"rotation": (rx, ry, rz)},
            label=f"{node.label} rotate_inst" if node.label else "rotate_inst",
        )
    return _apply


def scale_instances(sx: float = 1, sy: float = 1, sz: float = 1) -> Op:
    """Scale instances in-place."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeScaleInstances",
            child=node,
            properties={"scale": (sx, sy, sz)},
            label=f"{node.label} scale_inst" if node.label else "scale_inst",
        )
    return _apply


def translate_instances(x: float = 0, y: float = 0, z: float = 0) -> Op:
    """Translate instances in-place."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeTranslateInstances",
            child=node,
            properties={"translation": (x, y, z)},
            label=f"{node.label} translate_inst" if node.label else "translate_inst",
        )
    return _apply


def geometry_to_instance() -> Op:
    """Convert each input geometry into an instance (faster than Join Geometry for large inputs)."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeGeometryToInstance",
            child=node,
            label=f"{node.label} geo_to_inst" if node.label else "geometry_to_instance",
        )
    return _apply


def instances_to_points(
    position: tuple[float, float, float] = (0.0, 0.0, 0.0),
    radius: float = 0.05,
) -> Op:
    """Generate points at the origins of instances."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeInstancesToPoints",
            child=node,
            properties={"position": position, "radius": radius},
            label=f"{node.label} inst_to_pts" if node.label else "instances_to_points",
        )
    return _apply


def split_to_instances(group_id: int = 0) -> Op:
    """Split geometry into separate instances by group ID."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSplitToInstances",
            child=node,
            properties={"group_id": group_id},
            label=f"{node.label} split_inst" if node.label else "split_to_instances",
        )
    return _apply


def set_instance_transform() -> Op:
    """Set the transform matrix of instances."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSetInstanceTransform",
            child=node,
            label=f"{node.label} set_inst_xform" if node.label else "set_instance_transform",
        )
    return _apply
