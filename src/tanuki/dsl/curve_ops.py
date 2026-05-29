"""Curve operations — fill, fillet, resample, reverse, subdivide, trim, set attrs, and more."""

from __future__ import annotations

from collections.abc import Callable

from ..ir.nodes import IRGeometryOp, IRNode

Op = Callable[[IRNode], IRNode]


def fill_curve() -> Op:
    """Fill closed curves to generate mesh faces.

    ``GeometryNodeFillCurve`` only has a "Curve" input and a "Mesh" output —
    there is no "Group ID" socket.  The old ``group_id`` parameter caused the
    compiler to emit ``node.inputs["Group ID"]`` which raised a ``KeyError``
    inside Blender, crashing ``setup()`` and leaving the object as a flat plane.
    """
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeFillCurve",
            child=node,
            properties={},
            label=f"{node.label} fill" if node.label else "fill_curve",
        )
    return _apply


def fillet_curve(
    count: int = 1,
    radius: float = 0.25,
    limit_radius: bool = False,
) -> Op:
    """Round curve corners with circular arcs."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeFilletCurve",
            child=node,
            properties={
                "count": count,
                "radius": radius,
                "limit_radius": limit_radius,
            },
            label=f"{node.label} fillet" if node.label else "fillet_curve",
        )
    return _apply


def resample_curve(count: int = 10) -> Op:
    """Resample curves to a given number of points."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeResampleCurve",
            child=node,
            properties={"count": count},
            label=f"{node.label} resample" if node.label else "resample_curve",
        )
    return _apply


def reverse_curve() -> Op:
    """Reverse the direction of curves."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeReverseCurve",
            child=node,
            label=f"{node.label} reverse" if node.label else "reverse_curve",
        )
    return _apply


def subdivide_curve(cuts: int = 1) -> Op:
    """Subdivide curve segments."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSubdivideCurve",
            child=node,
            properties={"cuts": cuts},
            label=f"{node.label} subdivide" if node.label else "subdivide_curve",
        )
    return _apply


def trim_curve(start: float = 0.0, end: float = 1.0) -> Op:
    """Trim a curve by factor (0–1)."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeTrimCurve",
            child=node,
            properties={"start": start, "end": end},
            label=f"{node.label} trim" if node.label else "trim_curve",
        )
    return _apply


def curve_to_points(count: int = 10) -> Op:
    """Sample points along curves."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeCurveToPoints",
            child=node,
            properties={"count": count},
            label=f"{node.label} to_points" if node.label else "curve_to_points",
        )
    return _apply


def deform_curves_on_surface() -> Op:
    """Deform curves based on surface changes."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeDeformCurvesOnSurface",
            child=node,
            label=f"{node.label} deform_on_surface" if node.label else "deform_curves_on_surface",
        )
    return _apply


def sample_curve(factor: float = 0.0, curve_index: int = 0) -> Op:
    """Sample data at a position along a curve."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSampleCurve",
            child=node,
            properties={"factor": factor, "curve_index": curve_index},
            label=f"{node.label} sample" if node.label else "sample_curve",
        )
    return _apply


# ---------------------------------------------------------------------------
# Curve attribute setters
# ---------------------------------------------------------------------------


def set_curve_normal(
    normal: tuple[float, float, float] = (0.0, 0.0, 1.0),
) -> Op:
    """Set the normal evaluation mode for curve normals."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSetCurveNormal",
            child=node,
            properties={"normal": normal},
            label=f"{node.label} set_normal" if node.label else "set_curve_normal",
        )
    return _apply


def set_curve_radius(radius: float = 0.005) -> Op:
    """Set the radius at each curve control point."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSetCurveRadius",
            child=node,
            properties={"radius": radius},
            label=f"{node.label} set_radius" if node.label else "set_curve_radius",
        )
    return _apply


def set_curve_tilt(tilt: float = 0.0) -> Op:
    """Set the tilt angle at each curve control point."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSetCurveTilt",
            child=node,
            properties={"tilt": tilt},
            label=f"{node.label} set_tilt" if node.label else "set_curve_tilt",
        )
    return _apply


def set_handle_positions(
    position: tuple[float, float, float] = (0.0, 0.0, 0.0),
    offset: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> Op:
    """Set Bézier curve handle positions."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSetCurveHandlePositions",
            child=node,
            properties={"position": position, "offset": offset},
            label=f"{node.label} set_handles" if node.label else "set_handle_positions",
        )
    return _apply


def set_handle_type(handle_type: str = "AUTO") -> Op:
    """Set the handle type for Bézier curve control points.

    handle_type: 'FREE', 'AUTO', 'VECTOR', or 'ALIGN'.
    """
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeCurveSetHandles",
            child=node,
            properties={"handle_type": handle_type},
            label=f"{node.label} set_handle_type" if node.label else "set_handle_type",
        )
    return _apply


def set_spline_cyclic(cyclic: bool = False) -> Op:
    """Set whether each spline loops back on itself."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSetSplineCyclic",
            child=node,
            properties={"cyclic": cyclic},
            label=f"{node.label} set_cyclic" if node.label else "set_spline_cyclic",
        )
    return _apply


def set_spline_resolution(resolution: int = 12) -> Op:
    """Set the evaluated-point resolution for curve segments."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSetSplineResolution",
            child=node,
            properties={"resolution": resolution},
            label=f"{node.label} set_resolution" if node.label else "set_spline_resolution",
        )
    return _apply


def set_spline_type(spline_type: str = "POLY") -> Op:
    """Change the type of curves.

    spline_type: 'CATMULL_ROM', 'POLY', 'BEZIER', or 'NURBS'.
    """
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeCurveSplineType",
            child=node,
            properties={"spline_type": spline_type},
            label=f"{node.label} set_spline_type" if node.label else "set_spline_type",
        )
    return _apply


# ---------------------------------------------------------------------------
# Batch 3 — remaining curve operations
# ---------------------------------------------------------------------------


def edge_paths_to_curves(
    start_vertices: bool = True,
    next_vertex_index: int = -1,
) -> Op:
    """Output curves following paths across mesh edges."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeEdgePathsToCurves",
            child=node,
            properties={
                "start_vertices": start_vertices,
                "next_vertex_index": next_vertex_index,
            },
            label=f"{node.label} edge_paths" if node.label else "edge_paths_to_curves",
        )
    return _apply


def interpolate_curves(
    guide_up: tuple[float, float, float] = (0.0, 0.0, 0.0),
    guide_group_id: int = 0,
    points: IRNode | None = None,
    point_up: tuple[float, float, float] = (0.0, 0.0, 0.0),
    point_group_id: int = 0,
    max_neighbors: int = 4,
) -> Op:
    """Generate new curves on points by interpolating between existing guide curves."""
    def _apply(node: IRNode) -> IRGeometryOp:
        extra: dict[str, IRNode] = {}
        if points is not None:
            extra["Points"] = points
        return IRGeometryOp(
            op_type="GeometryNodeInterpolateCurves",
            child=node,
            properties={
                "guide_up": guide_up,
                "guide_group_id": guide_group_id,
                "point_up": point_up,
                "point_group_id": point_group_id,
                "max_neighbors": max_neighbors,
            },
            extra_children=extra,
            label=f"{node.label} interpolate" if node.label else "interpolate_curves",
        )
    return _apply


def points_to_curves(
    curve_group_id: int = 0,
    weight: float = 0.0,
) -> Op:
    """Convert points to curves, split by group ID and ordered by weight."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodePointsToCurves",
            child=node,
            properties={
                "curve_group_id": curve_group_id,
                "weight": weight,
            },
            label=f"{node.label} to_curves" if node.label else "points_to_curves",
        )
    return _apply


def curves_to_grease_pencil(
    instances_as_layers: bool = True,
) -> Op:
    """Convert curves into a Grease Pencil layer."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeCurvesToGreasePencil",
            child=node,
            properties={"instances_as_layers": instances_as_layers},
            label=f"{node.label} to_gp" if node.label else "curves_to_grease_pencil",
        )
    return _apply


def grease_pencil_to_curves(
    layers_as_instances: bool = True,
) -> Op:
    """Convert Grease Pencil layers into curve instances."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeGreasePencilToCurves",
            child=node,
            properties={"layers_as_instances": layers_as_instances},
            label=f"{node.label} gp_to_curves" if node.label else "grease_pencil_to_curves",
        )
    return _apply


def string_to_curves(
    string: str = "",
    size: float = 1.0,
    character_spacing: float = 1.0,
    word_spacing: float = 1.0,
    line_spacing: float = 1.0,
    text_box_width: float = 0.0,
    text_box_height: float = 0.0,
) -> Op:
    """Generate a paragraph of text as curve instances."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeStringToCurves",
            child=node,
            properties={
                "string": string,
                "size": size,
                "character_spacing": character_spacing,
                "word_spacing": word_spacing,
                "line_spacing": line_spacing,
                "text_box_width": text_box_width,
                "text_box_height": text_box_height,
            },
            label=f"{node.label} string_to_curves" if node.label else "string_to_curves",
        )
    return _apply
