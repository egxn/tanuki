"""Volume operations — distribute points in volume, points to volume, volume cube."""

from __future__ import annotations

from collections.abc import Callable

from ..ir.nodes import IRGeometryOp, IRNode, IRPrimitive, PrimitiveType

Op = Callable[[IRNode], IRNode]


def distribute_points_in_volume(
    density: float = 1.0,
    seed: int = 0,
    spacing: tuple[float, float, float] = (0.3, 0.3, 0.3),
    threshold: float = 0.1,
) -> Op:
    """Generate points inside a volume."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeDistributePointsInVolume",
            child=node,
            properties={
                "density": density,
                "seed": seed,
                "spacing": spacing,
                "threshold": threshold,
            },
            label=f"{node.label} dist_pts_vol" if node.label else "distribute_points_in_volume",
        )
    return _apply


def points_to_volume(
    density: float = 1.0,
    voxel_size: float = 0.3,
    voxel_amount: float = 64.0,
    radius: float = 0.5,
) -> Op:
    """Generate a fog volume sphere around every point."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodePointsToVolume",
            child=node,
            properties={
                "density": density,
                "voxel_size": voxel_size,
                "voxel_amount": voxel_amount,
                "radius": radius,
            },
            label=f"{node.label} pts_to_vol" if node.label else "points_to_volume",
        )
    return _apply


def volume_cube(
    density: float = 1.0,
    background: float = 0.0,
    min: tuple[float, float, float] = (-1.0, -1.0, -1.0),
    max: tuple[float, float, float] = (1.0, 1.0, 1.0),
    resolution_x: int = 32,
    resolution_y: int = 32,
    resolution_z: int = 32,
    label: str = "",
) -> IRPrimitive:
    """Create a dense volume cube primitive."""
    return IRPrimitive(
        primitive_type=PrimitiveType.VOLUME_CUBE,
        label=label,
        properties={
            "density": density,
            "background": background,
            "min": min,
            "max": max,
            "resolution_x": resolution_x,
            "resolution_y": resolution_y,
            "resolution_z": resolution_z,
        },
    )
