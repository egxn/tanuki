"""Mesh operations — extrude, subdivide, shade smooth, merge by distance, and more."""

from __future__ import annotations

from collections.abc import Callable

from ..ir.nodes import IRGeometryOp, IRNode

Op = Callable[[IRNode], IRNode]


def extrude(offset_scale: float = 1.0, individual: bool = False) -> Op:
    """Extrude mesh faces."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeExtrudeMesh",
            child=node,
            properties={
                "mode": "INDIVIDUAL" if individual else "FACES",
                "offset_scale": offset_scale,
            },
            label=f"{node.label} extrude" if node.label else "extrude",
        )
    return _apply


def subdivide(level: int = 1) -> Op:
    """Subdivide mesh."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSubdivideMesh",
            child=node,
            properties={"level": level},
            label=f"{node.label} subdivide" if node.label else "subdivide",
        )
    return _apply


def subdivide_surface(level: int = 1) -> Op:
    """Subdivision surface (smooth)."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSubdivisionSurface",
            child=node,
            properties={"level": level},
            label=f"{node.label} subdiv_surface" if node.label else "subdiv_surface",
        )
    return _apply


def set_shade_smooth(shade_smooth: bool = True) -> Op:
    """Set shade smooth on geometry."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSetShadeSmooth",
            child=node,
            properties={"shade_smooth": shade_smooth},
            label=f"{node.label} shade_smooth" if node.label else "shade_smooth",
        )
    return _apply


def merge_by_distance(distance: float = 0.001) -> Op:
    """Merge vertices by distance."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeMergeByDistance",
            child=node,
            properties={"distance": distance},
            label=f"{node.label} merge" if node.label else "merge",
        )
    return _apply


# ---------------------------------------------------------------------------
# New mesh operations
# ---------------------------------------------------------------------------


def dual_mesh(keep_boundaries: bool = False) -> Op:
    """Create a dual mesh."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeDualMesh",
            child=node,
            properties={"keep_boundaries": keep_boundaries},
            label=f"{node.label} dual" if node.label else "dual_mesh",
        )
    return _apply


def mesh_to_curve() -> Op:
    """Convert mesh edges to curves."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeMeshToCurve",
            child=node,
            label=f"{node.label} to_curve" if node.label else "mesh_to_curve",
        )
    return _apply


def mesh_to_points(radius: float = 0.05, mode: str = "VERTICES") -> Op:
    """Convert mesh elements to points."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeMeshToPoints",
            child=node,
            properties={"mode": mode, "radius": radius},
            label=f"{node.label} to_points" if node.label else "mesh_to_points",
        )
    return _apply


def mesh_to_volume(
    density: float = 1.0,
    voxel_size: float = 0.3,
    voxel_amount: float = 64.0,
    interior_band_width: float = 0.2,
) -> Op:
    """Convert mesh to volume."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeMeshToVolume",
            child=node,
            properties={
                "density": density,
                "voxel_size": voxel_size,
                "voxel_amount": voxel_amount,
                "interior_band_width": interior_band_width,
            },
            label=f"{node.label} to_volume" if node.label else "mesh_to_volume",
        )
    return _apply


def volume_to_mesh(
    threshold: float = 0.1,
    adaptivity: float = 0.0,
    voxel_size: float = 0.3,
    voxel_amount: float = 64.0,
) -> Op:
    """Convert volume to mesh."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeVolumeToMesh",
            child=node,
            properties={
                "threshold": threshold,
                "adaptivity": adaptivity,
                "voxel_size": voxel_size,
                "voxel_amount": voxel_amount,
            },
            label=f"{node.label} vol_to_mesh" if node.label else "volume_to_mesh",
        )
    return _apply


def set_mesh_normal(
    remove_custom: bool = True,
    edge_sharpness: bool = False,
    face_sharpness: bool = False,
) -> Op:
    """Set mesh normals."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSetMeshNormal",
            child=node,
            properties={
                "remove_custom": remove_custom,
                "edge_sharpness": edge_sharpness,
                "face_sharpness": face_sharpness,
            },
            label=f"{node.label} set_normal" if node.label else "set_mesh_normal",
        )
    return _apply


def curve_to_mesh(
    profile: IRNode | None = None,
    scale: float = 1.0,
    fill_caps: bool = False,
) -> Op:
    """Convert curves to mesh, optionally with a profile shape."""
    def _apply(node: IRNode) -> IRGeometryOp:
        extra = {"Profile Curve": profile} if profile is not None else {}
        return IRGeometryOp(
            op_type="GeometryNodeCurveToMesh",
            child=node,
            properties={"profile_scale": scale, "fill_caps": fill_caps},
            extra_children=extra,
            label=f"{node.label} to_mesh" if node.label else "curve_to_mesh",
        )
    return _apply
