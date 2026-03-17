"""Other geometry operations — convex hull, delete, distribute points, duplicate, flip, scale, split, triangulate, bounding box, separate, set id, set point radius, sort elements."""

from __future__ import annotations

from collections.abc import Callable

from ..ir.nodes import IRGeometryOp, IRNode, IRSeparateComponents

Op = Callable[[IRNode], IRNode]


def convex_hull() -> Op:
    """Compute the convex hull of a geometry."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeConvexHull",
            child=node,
            properties={},
            label=f"{node.label} convex_hull" if node.label else "convex_hull",
        )
    return _apply


def delete_geometry(mode: str = "ALL", domain: str = "POINT") -> Op:
    """Remove selected elements of a geometry."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeDeleteGeometry",
            child=node,
            properties={"mode": mode, "domain": domain},
            label=f"{node.label} delete" if node.label else "delete_geometry",
        )
    return _apply


def distribute_points_on_faces(
    density: float = 10.0,
    density_max: float = 10.0,
    density_factor: float = 1.0,
    distance_min: float = 0.0,
    seed: int = 0,
    distribute_method: str = "RANDOM",
) -> Op:
    """Generate points spread out on the surface of a mesh."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeDistributePointsOnFaces",
            child=node,
            properties={
                "density": density,
                "density_max": density_max,
                "density_factor": density_factor,
                "distance_min": distance_min,
                "seed": seed,
                "distribute_method": distribute_method,
            },
            label=f"{node.label} dist_pts" if node.label else "distribute_points_on_faces",
        )
    return _apply


def duplicate_elements(amount: int = 1, domain: str = "POINT") -> Op:
    """Generate copies of each selected input element."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeDuplicateElements",
            child=node,
            properties={"amount": amount, "domain": domain},
            label=f"{node.label} duplicate" if node.label else "duplicate_elements",
        )
    return _apply


def flip_faces() -> Op:
    """Reverse the normal direction of selected faces."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeFlipFaces",
            child=node,
            properties={},
            label=f"{node.label} flip" if node.label else "flip_faces",
        )
    return _apply


def scale_elements(
    scale: float = 1.0,
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
    domain: str = "FACE",
    scale_mode: str = "UNIFORM",
) -> Op:
    """Scale mesh elements (faces or edges)."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeScaleElements",
            child=node,
            properties={
                "element_scale": scale,
                "center": center,
                "axis": axis,
                "domain": domain,
                "scale_mode": scale_mode,
            },
            label=f"{node.label} scale_el" if node.label else "scale_elements",
        )
    return _apply


def split_edges() -> Op:
    """Split the edges of a mesh."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSplitEdges",
            child=node,
            properties={},
            label=f"{node.label} split_edges" if node.label else "split_edges",
        )
    return _apply


def triangulate(quad_method: str = "BEAUTY", ngon_method: str = "BEAUTY") -> Op:
    """Convert all faces in a mesh to triangular faces."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeTriangulate",
            child=node,
            properties={"quad_method": quad_method, "ngon_method": ngon_method},
            label=f"{node.label} triangulate" if node.label else "triangulate",
        )
    return _apply


def bounding_box(use_radius: bool = True) -> Op:
    """Compute the bounding box of a geometry."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeBoundBox",
            child=node,
            properties={"use_radius": use_radius},
            label=f"{node.label} bbox" if node.label else "bounding_box",
        )
    return _apply


def separate_components(component: str = "Mesh") -> Op:
    """Separate geometry into components (Mesh, Curve, Grease Pencil, Point Cloud, Volume, Instances)."""
    def _apply(node: IRNode) -> IRSeparateComponents:
        return IRSeparateComponents(
            child=node,
            component=component,
            label=f"{node.label} sep_{component.lower()}" if node.label else f"separate_{component.lower()}",
        )
    return _apply


def separate_geometry() -> Op:
    """Separate geometry by selection (outputs the selected part)."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSeparateGeometry",
            child=node,
            properties={},
            label=f"{node.label} sep_geo" if node.label else "separate_geometry",
        )
    return _apply


def set_id(id_value: int = 0) -> Op:
    """Set the ID attribute on geometry elements."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSetID",
            child=node,
            properties={"id_value": id_value},
            label=f"{node.label} set_id" if node.label else "set_id",
        )
    return _apply


def set_point_radius(radius: float = 0.05) -> Op:
    """Set the radius of point cloud points."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSetPointRadius",
            child=node,
            properties={"radius": radius},
            label=f"{node.label} set_pt_rad" if node.label else "set_point_radius",
        )
    return _apply


def sort_elements(
    sort_weight: float = 0.0,
    group_id: int = 0,
    domain: str = "POINT",
) -> Op:
    """Sort geometry elements by weight."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSortElements",
            child=node,
            properties={
                "sort_weight": sort_weight,
                "group_id": group_id,
                "domain": domain,
            },
            label=f"{node.label} sort" if node.label else "sort_elements",
        )
    return _apply


def points_to_vertices() -> Op:
    """Generate a mesh vertex for each point cloud point."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodePointsToVertices",
            child=node,
            properties={},
            label=f"{node.label} pts_to_verts" if node.label else "points_to_vertices",
        )
    return _apply


def set_geometry_name(name: str = "") -> Op:
    """Set the name of a geometry for easier debugging."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSetGeometryName",
            child=node,
            properties={"name": name},
            label=f"{node.label} set_name" if node.label else "set_geometry_name",
        )
    return _apply


def set_face_set(face_set: int = 0) -> Op:
    """Set sculpt face set values for faces."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeToolSetFaceSet",
            child=node,
            properties={"face_set": face_set},
            label=f"{node.label} set_face_set" if node.label else "set_face_set",
        )
    return _apply


def set_selection(domain: str = "POINT", selection_type: str = "BOOLEAN") -> Op:
    """Set selection of the edited geometry, for tool execution."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeToolSetSelection",
            child=node,
            properties={"domain": domain, "selection_type": selection_type},
            label=f"{node.label} set_sel" if node.label else "set_selection",
        )
    return _apply


def merge_layers(mode: str = "MERGE_BY_NAME", group_id: int = 0) -> Op:
    """Join groups of Grease Pencil layers into one."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeMergeLayers",
            child=node,
            properties={"mode": mode, "group_id": group_id},
            label=f"{node.label} merge_layers" if node.label else "merge_layers",
        )
    return _apply


def set_grease_pencil_depth(depth_order: str = "2D") -> Op:
    """Set the Grease Pencil depth order to use."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSetGreasePencilDepth",
            child=node,
            properties={"depth_order": depth_order},
            label=f"{node.label} set_gp_depth" if node.label else "set_grease_pencil_depth",
        )
    return _apply


def set_grease_pencil_softness(softness: float = 0.0) -> Op:
    """Set softness attribute on Grease Pencil geometry."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSetGreasePencilSoftness",
            child=node,
            properties={"softness": softness},
            label=f"{node.label} set_gp_soft" if node.label else "set_grease_pencil_softness",
        )
    return _apply


def switch(switch_value: bool = False, true_child: IRNode | None = None) -> Op:
    """Switch between two geometries based on a boolean condition.

    The geometry piped in becomes the 'False' input; *true_child* is the 'True' input.
    """
    def _apply(node: IRNode) -> IRGeometryOp:
        extra = {"True": true_child} if true_child is not None else {}
        return IRGeometryOp(
            op_type="GeometryNodeSwitch",
            child=node,
            properties={"switch": switch_value, "input_type": "GEOMETRY"},
            extra_children=extra,
            label=f"{node.label} switch" if node.label else "switch",
        )
    return _apply


def get_named_grid(name: str = "", remove: bool = True, data_type: str = "FLOAT") -> Op:
    """Get a named volume grid."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeGetNamedGrid",
            child=node,
            properties={"name": name, "remove": remove, "data_type": data_type},
            label=f"{node.label} get_grid" if node.label else "get_named_grid",
        )
    return _apply


def store_named_grid(name: str = "", grid_value: float = 0.0, data_type: str = "FLOAT") -> Op:
    """Store grid data in a named volume grid."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeStoreNamedGrid",
            child=node,
            properties={"name": name, "grid_value": grid_value, "data_type": data_type},
            label=f"{node.label} store_grid" if node.label else "store_named_grid",
        )
    return _apply


def set_grease_pencil_color(
    color: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
    opacity: float = 1.0,
) -> Op:
    """Set color and opacity on Grease Pencil geometry."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSetGreasePencilColor",
            child=node,
            properties={"color": color, "opacity": opacity},
            label=f"{node.label} set_gp_color" if node.label else "set_grease_pencil_color",
        )
    return _apply


def viewer(value: float = 0.0, data_type: str = "FLOAT", domain: str = "AUTO") -> Op:
    """Display geometry in the Spreadsheet Editor (debugging pass-through)."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeViewer",
            child=node,
            properties={"value": value, "data_type": data_type, "domain": domain},
            label=f"{node.label} viewer" if node.label else "viewer",
        )
    return _apply


# ---------------------------------------------------------------------------
# Batch 14 — Info / Query nodes
# ---------------------------------------------------------------------------


def curve_length() -> Op:
    """Retrieve the total length of all splines in a curve."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeCurveLength",
            child=node,
            properties={},
            label=f"{node.label} curve_length" if node.label else "curve_length",
        )
    return _apply


def domain_size() -> Op:
    """Retrieve the number of elements per attribute domain (point, edge, face, …)."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeAttributeDomainSize",
            child=node,
            properties={},
            label=f"{node.label} domain_size" if node.label else "domain_size",
        )
    return _apply


def geometry_proximity(
    target_element: str = "FACES",
    sample_position: tuple[float, float, float] | None = None,
    sample_group_id: int = 0,
    group_id: int = 0,
) -> Op:
    """Compute the closest location on the target geometry."""
    def _apply(node: IRNode) -> IRGeometryOp:
        props: dict = {"target_element": target_element, "group_id": group_id, "sample_group_id": sample_group_id}
        if sample_position is not None:
            props["sample_position"] = sample_position
        return IRGeometryOp(
            op_type="GeometryNodeProximity",
            child=node,
            properties=props,
            label=f"{node.label} proximity" if node.label else "geometry_proximity",
        )
    return _apply


def sample_nearest(
    domain: str = "POINT",
    sample_position: tuple[float, float, float] | None = None,
) -> Op:
    """Find the closest element of a geometry to a position."""
    def _apply(node: IRNode) -> IRGeometryOp:
        props: dict = {"domain": domain}
        if sample_position is not None:
            props["sample_position"] = sample_position
        return IRGeometryOp(
            op_type="GeometryNodeSampleNearest",
            child=node,
            properties=props,
            label=f"{node.label} sample_nearest" if node.label else "sample_nearest",
        )
    return _apply


def sample_index(
    value: float = 0.0,
    index: int = 0,
    data_type: str = "FLOAT",
    domain: str = "POINT",
    clamp: bool = False,
) -> Op:
    """Retrieve values from specific geometry elements by index."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeSampleIndex",
            child=node,
            properties={
                "value": value,
                "index": index,
                "data_type": data_type,
                "domain": domain,
                "clamp": clamp,
            },
            label=f"{node.label} sample_index" if node.label else "sample_index",
        )
    return _apply


def attribute_statistic(
    attribute: float = 0.0,
    data_type: str = "FLOAT",
    domain: str = "POINT",
) -> Op:
    """Calculate statistics (mean, median, sum, …) of an attribute over a geometry."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeAttributeStatistic",
            child=node,
            properties={"attribute": attribute, "data_type": data_type, "domain": domain},
            label=f"{node.label} attr_stat" if node.label else "attribute_statistic",
        )
    return _apply


# ---------------------------------------------------------------------------
# Batch 15 — Sampling + Grid conversion nodes
# ---------------------------------------------------------------------------


def raycast(
    attribute: float = 0.0,
    source_position: tuple[float, float, float] | None = None,
    ray_direction: tuple[float, float, float] = (0.0, 0.0, -1.0),
    ray_length: float = 100.0,
    data_type: str = "FLOAT",
) -> Op:
    """Cast rays onto a target geometry and retrieve hit information."""
    def _apply(node: IRNode) -> IRGeometryOp:
        props: dict = {
            "attribute": attribute,
            "ray_direction": ray_direction,
            "ray_length": ray_length,
            "data_type": data_type,
        }
        if source_position is not None:
            props["source_position"] = source_position
        return IRGeometryOp(
            op_type="GeometryNodeRaycast",
            child=node,
            properties=props,
            label=f"{node.label} raycast" if node.label else "raycast",
        )
    return _apply


def sample_nearest_surface(
    value: float = 0.0,
    sample_position: tuple[float, float, float] | None = None,
    data_type: str = "FLOAT",
    group_id: int = 0,
    sample_group_id: int = 0,
) -> Op:
    """Interpolate a mesh attribute at the closest surface point."""
    def _apply(node: IRNode) -> IRGeometryOp:
        props: dict = {
            "value": value,
            "data_type": data_type,
            "group_id": group_id,
            "sample_group_id": sample_group_id,
        }
        if sample_position is not None:
            props["sample_position"] = sample_position
        return IRGeometryOp(
            op_type="GeometryNodeSampleNearestSurface",
            child=node,
            properties=props,
            label=f"{node.label} sample_surface" if node.label else "sample_nearest_surface",
        )
    return _apply


def sample_uv_surface(
    value: float = 0.0,
    uv_map: tuple[float, float, float] | None = None,
    sample_uv: tuple[float, float, float] | None = None,
    data_type: str = "FLOAT",
) -> Op:
    """Interpolate a mesh attribute at a UV coordinate."""
    def _apply(node: IRNode) -> IRGeometryOp:
        props: dict = {"value": value, "data_type": data_type}
        if uv_map is not None:
            props["uv_map"] = uv_map
        if sample_uv is not None:
            props["sample_uv"] = sample_uv
        return IRGeometryOp(
            op_type="GeometryNodeSampleUVSurface",
            child=node,
            properties=props,
            label=f"{node.label} sample_uv" if node.label else "sample_uv_surface",
        )
    return _apply


def mesh_to_sdf_grid(
    voxel_size: float = 0.3,
    band_width: int = 3,
) -> Op:
    """Create a signed distance field grid from a mesh."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeMeshToSDFGrid",
            child=node,
            properties={"voxel_size": voxel_size, "band_width": band_width},
            label=f"{node.label} sdf_grid" if node.label else "mesh_to_sdf_grid",
        )
    return _apply


def mesh_to_density_grid(
    density: float = 1.0,
    voxel_size: float = 0.3,
    gradient_width: float = 0.2,
) -> Op:
    """Create a density volume grid from a mesh."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeMeshToDensityGrid",
            child=node,
            properties={"density": density, "voxel_size": voxel_size, "gradient_width": gradient_width},
            label=f"{node.label} density_grid" if node.label else "mesh_to_density_grid",
        )
    return _apply


def distribute_points_in_grid(
    density: float = 1.0,
    seed: int = 0,
    spacing: tuple[float, float, float] | None = None,
    threshold: float = 0.1,
    mode: str = "DENSITY_RANDOM",
) -> Op:
    """Distribute points inside a volume grid.

    *mode*: ``"DENSITY_RANDOM"`` | ``"DENSITY_GRID"``
    """
    def _apply(node: IRNode) -> IRGeometryOp:
        props: dict = {"density": density, "seed": seed, "threshold": threshold, "mode": mode}
        if spacing is not None:
            props["spacing"] = spacing
        return IRGeometryOp(
            op_type="GeometryNodeDistributePointsInGrid",
            child=node,
            properties=props,
            label=f"{node.label} dist_grid" if node.label else "distribute_points_in_grid",
        )
    return _apply


def grid_to_mesh(
    threshold: float = 0.1,
    adaptivity: float = 0.0,
) -> Op:
    """Convert a volume grid to a mesh."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeGridToMesh",
            child=node,
            properties={"threshold": threshold, "adaptivity": adaptivity},
            label=f"{node.label} grid_to_mesh" if node.label else "grid_to_mesh",
        )
    return _apply


def points_to_sdf_grid(
    radius: float = 0.5,
    voxel_size: float = 0.3,
) -> Op:
    """Convert points to a signed distance field grid."""
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodePointsToSDFGrid",
            child=node,
            properties={"radius": radius, "voxel_size": voxel_size},
            label=f"{node.label} pts_sdf" if node.label else "points_to_sdf_grid",
        )
    return _apply
