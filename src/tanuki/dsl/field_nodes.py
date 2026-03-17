"""Field input nodes — topology queries and per-element data.

Field nodes produce values (scalar, vector, integer) that are evaluated
per-element inside a Geometry Nodes context.  They have **no geometry
input** — they are wired into input sockets of other nodes.
"""

from __future__ import annotations

from ..ir.nodes import IRFieldInput


# ---------------------------------------------------------------------------
# Geometry / generic fields
# ---------------------------------------------------------------------------


def position() -> IRFieldInput:
    """Per-element position vector."""
    return IRFieldInput(
        field_type="GeometryNodeInputPosition",
        output_socket="Position",
        label="position",
    )


def normal() -> IRFieldInput:
    """Per-face / per-vertex normal vector."""
    return IRFieldInput(
        field_type="GeometryNodeInputNormal",
        output_socket="Normal",
        label="normal",
    )


def index() -> IRFieldInput:
    """Per-element index (0, 1, 2, …)."""
    return IRFieldInput(
        field_type="GeometryNodeInputIndex",
        output_socket="Index",
        label="index",
    )


def id_field() -> IRFieldInput:
    """Per-element ID attribute."""
    return IRFieldInput(
        field_type="GeometryNodeInputID",
        output_socket="ID",
        label="id",
    )


# ---------------------------------------------------------------------------
# Mesh edge topology
# ---------------------------------------------------------------------------


def edge_vertices(output: str = "Position 1") -> IRFieldInput:
    """Edge topology — vertex positions and indices of each edge.

    *output* selects the socket:
    ``"Position 1"``, ``"Position 2"``, ``"Vertex Index 1"``, ``"Vertex Index 2"``.
    """
    return IRFieldInput(
        field_type="GeometryNodeInputMeshEdgeVertices",
        output_socket=output,
        label="edge_vertices",
    )


def edge_angle(unsigned: bool = True) -> IRFieldInput:
    """Angle between the two faces that share an edge.

    *unsigned* selects ``"Unsigned Angle"`` (always positive) or
    ``"Signed Angle"`` (includes concavity sign).
    """
    return IRFieldInput(
        field_type="GeometryNodeInputMeshEdgeAngle",
        output_socket="Unsigned Angle" if unsigned else "Signed Angle",
        label="edge_angle",
    )


# ---------------------------------------------------------------------------
# Mesh vertex topology
# ---------------------------------------------------------------------------


def vertex_neighbors(output: str = "Vertex Count") -> IRFieldInput:
    """Number of vertices / faces connected to each vertex.

    *output*: ``"Vertex Count"`` or ``"Face Count"``.
    """
    return IRFieldInput(
        field_type="GeometryNodeInputMeshVertexNeighbors",
        output_socket=output,
        label="vertex_neighbors",
    )


# ---------------------------------------------------------------------------
# Mesh face topology
# ---------------------------------------------------------------------------


def face_neighbors(output: str = "Vertex Count") -> IRFieldInput:
    """Number of vertices / neighboring faces of each face.

    *output*: ``"Vertex Count"`` or ``"Face Count"``.
    """
    return IRFieldInput(
        field_type="GeometryNodeInputMeshFaceNeighbors",
        output_socket=output,
        label="face_neighbors",
    )


def face_area() -> IRFieldInput:
    """Area of each face."""
    return IRFieldInput(
        field_type="GeometryNodeInputMeshFaceArea",
        output_socket="Area",
        label="face_area",
    )


# ---------------------------------------------------------------------------
# Mesh edge-neighbor topology
# ---------------------------------------------------------------------------


def edge_neighbors() -> IRFieldInput:
    """Number of faces connected to each edge."""
    return IRFieldInput(
        field_type="GeometryNodeInputMeshEdgeNeighbors",
        output_socket="Face Count",
        label="edge_neighbors",
    )


# ---------------------------------------------------------------------------
# Mesh island topology
# ---------------------------------------------------------------------------


def mesh_island(output: str = "Island Index") -> IRFieldInput:
    """Mesh island index and total count.

    *output*: ``"Island Index"`` or ``"Island Count"``.
    """
    return IRFieldInput(
        field_type="GeometryNodeInputMeshIsland",
        output_socket=output,
        label="mesh_island",
    )


# ---------------------------------------------------------------------------
# Named attribute
# ---------------------------------------------------------------------------


def named_attribute(name: str, data_type: str = "FLOAT") -> IRFieldInput:
    """Read a named attribute from the geometry.

    *data_type*: ``"FLOAT"``, ``"INT"``, ``"FLOAT_VECTOR"``, ``"FLOAT_COLOR"``, ``"BOOLEAN"``.
    """
    return IRFieldInput(
        field_type="GeometryNodeInputNamedAttribute",
        output_socket="Attribute",
        properties={"data_type": data_type, "name": name},
        label=f"attr:{name}",
    )


# ---------------------------------------------------------------------------
# Radius
# ---------------------------------------------------------------------------


def radius() -> IRFieldInput:
    """Per-element radius (point cloud / curve)."""
    return IRFieldInput(
        field_type="GeometryNodeInputRadius",
        output_socket="Radius",
        label="radius",
    )


# ---------------------------------------------------------------------------
# Mesh smoothness fields
# ---------------------------------------------------------------------------


def is_edge_smooth() -> IRFieldInput:
    """Whether each edge is marked smooth."""
    return IRFieldInput(
        field_type="GeometryNodeInputEdgeSmooth",
        output_socket="Smooth",
        label="is_edge_smooth",
    )


def is_face_planar(threshold: float = 0.01) -> IRFieldInput:
    """Whether each face is planar within *threshold*."""
    return IRFieldInput(
        field_type="GeometryNodeInputMeshFaceIsPlanar",
        output_socket="Planar",
        input_defaults={"Threshold": threshold},
        label="is_face_planar",
    )


def is_face_smooth() -> IRFieldInput:
    """Whether each face has smooth shading."""
    return IRFieldInput(
        field_type="GeometryNodeInputShadeSmooth",
        output_socket="Smooth",
        label="is_face_smooth",
    )


# ---------------------------------------------------------------------------
# Curve / spline info fields
# ---------------------------------------------------------------------------


def curve_tangent() -> IRFieldInput:
    """Per-point tangent direction on a curve."""
    return IRFieldInput(
        field_type="GeometryNodeInputTangent",
        output_socket="Tangent",
        label="curve_tangent",
    )


def curve_tilt() -> IRFieldInput:
    """Per-point tilt angle on a curve."""
    return IRFieldInput(
        field_type="GeometryNodeInputCurveTilt",
        output_socket="Tilt",
        label="curve_tilt",
    )


def is_spline_cyclic() -> IRFieldInput:
    """Whether each spline is cyclic (closed)."""
    return IRFieldInput(
        field_type="GeometryNodeInputSplineCyclic",
        output_socket="Cyclic",
        label="is_spline_cyclic",
    )


def spline_resolution() -> IRFieldInput:
    """Resolution of each spline."""
    return IRFieldInput(
        field_type="GeometryNodeInputSplineResolution",
        output_socket="Resolution",
        label="spline_resolution",
    )


def curve_handle_positions(
    relative: bool = False,
    output: str = "Left",
) -> IRFieldInput:
    """Handle positions of Bezier control points.

    *relative*: if ``True``, positions are relative to the control point.
    *output*: ``"Left"`` or ``"Right"``.
    """
    return IRFieldInput(
        field_type="GeometryNodeInputCurveHandlePositions",
        output_socket=output,
        input_defaults={"Relative": relative},
        label="curve_handle_positions",
    )


def endpoint_selection(
    start_size: int = 1,
    end_size: int = 1,
) -> IRFieldInput:
    """Select points near the start/end of each spline.

    *start_size*: number of points selected at the start.
    *end_size*: number of points selected at the end.
    """
    return IRFieldInput(
        field_type="GeometryNodeCurveEndpointSelection",
        output_socket="Selection",
        input_defaults={"Start Size": start_size, "End Size": end_size},
        label="endpoint_selection",
    )


def handle_type_selection(
    handle_type: str = "FREE",
    mode: str = "LEFT",
) -> IRFieldInput:
    """Select points by their Bezier handle type.

    *handle_type*: ``"FREE"``, ``"AUTO"``, ``"VECTOR"``, or ``"ALIGN"``.
    *mode*: ``"LEFT"``, ``"RIGHT"``, or both via set flags.
    """
    return IRFieldInput(
        field_type="GeometryNodeCurveHandleTypeSelection",
        output_socket="Selection",
        properties={"handle_type": handle_type, "mode": {mode}},
        label="handle_type_selection",
    )


def spline_length(output: str = "Length") -> IRFieldInput:
    """Length and point count of each spline.

    *output*: ``"Length"`` or ``"Point Count"``.
    """
    return IRFieldInput(
        field_type="GeometryNodeSplineLength",
        output_socket=output,
        label="spline_length",
    )


def spline_parameter(output: str = "Factor") -> IRFieldInput:
    """Parametric position along each spline.

    *output*: ``"Factor"`` (0–1), ``"Length"`` (distance), or ``"Index"`` (integer).
    """
    return IRFieldInput(
        field_type="GeometryNodeSplineParameter",
        output_socket=output,
        label="spline_parameter",
    )


# ---------------------------------------------------------------------------
# Curve topology queries
# ---------------------------------------------------------------------------


def curve_of_point(
    point_index: int = 0,
    output: str = "Curve Index",
) -> IRFieldInput:
    """Find which curve a point belongs to.

    *output*: ``"Curve Index"`` or ``"Index in Curve"``.
    """
    return IRFieldInput(
        field_type="GeometryNodeCurveOfPoint",
        output_socket=output,
        input_defaults={"Point Index": point_index},
        label="curve_of_point",
    )


def offset_point_in_curve(
    point_index: int = 0,
    offset: int = 0,
    output: str = "Is Valid Offset",
) -> IRFieldInput:
    """Offset a point index along its curve.

    *output*: ``"Is Valid Offset"`` (boolean) or ``"Point Index"`` (int).
    """
    return IRFieldInput(
        field_type="GeometryNodeOffsetPointInCurve",
        output_socket=output,
        input_defaults={"Point Index": point_index, "Offset": offset},
        label="offset_point_in_curve",
    )


def points_of_curve(
    curve_index: int = 0,
    weights: float = 0.0,
    sort_index: int = 0,
    output: str = "Point Index",
) -> IRFieldInput:
    """Get point indices of a curve.

    *output*: ``"Point Index"`` or ``"Total"``.
    """
    return IRFieldInput(
        field_type="GeometryNodePointsOfCurve",
        output_socket=output,
        input_defaults={
            "Curve Index": curve_index,
            "Weights": weights,
            "Sort Index": sort_index,
        },
        label="points_of_curve",
    )


# ---------------------------------------------------------------------------
# Shortest edge paths
# ---------------------------------------------------------------------------


def shortest_edge_paths(
    end_vertex: bool = False,
    edge_cost: float = 1.0,
    output: str = "Next Vertex Index",
) -> IRFieldInput:
    """Shortest paths from each vertex to end vertices.

    *output*: ``"Next Vertex Index"`` (int) or ``"Total Cost"`` (float).
    """
    return IRFieldInput(
        field_type="GeometryNodeInputShortestEdgePaths",
        output_socket=output,
        input_defaults={"End Vertex": end_vertex, "Edge Cost": edge_cost},
        label="shortest_edge_paths",
    )


# ---------------------------------------------------------------------------
# Instance info fields
# ---------------------------------------------------------------------------


def instance_rotation() -> IRFieldInput:
    """Rotation of each instance."""
    return IRFieldInput(
        field_type="GeometryNodeInputInstanceRotation",
        output_socket="Rotation",
        label="instance_rotation",
    )


def instance_scale() -> IRFieldInput:
    """Scale of each instance."""
    return IRFieldInput(
        field_type="GeometryNodeInputInstanceScale",
        output_socket="Scale",
        label="instance_scale",
    )


# ---------------------------------------------------------------------------
# Material info
# ---------------------------------------------------------------------------


def material_index() -> IRFieldInput:
    """Material index of each face."""
    return IRFieldInput(
        field_type="GeometryNodeInputMaterialIndex",
        output_socket="Material Index",
        label="material_index",
    )


# ---------------------------------------------------------------------------
# Material selection & input
# ---------------------------------------------------------------------------


def material_selection(material: str = "") -> IRFieldInput:
    """Select faces using a specific material.

    *material*: name of the material in ``bpy.data.materials``.
    """
    return IRFieldInput(
        field_type="GeometryNodeMaterialSelection",
        output_socket="Selection",
        input_defaults={"Material": ("MATERIAL", material)} if material else {},
        label="material_selection",
    )


def input_material(material: str = "") -> IRFieldInput:
    """Output a single material reference.

    *material*: name of the material in ``bpy.data.materials``.
    """
    return IRFieldInput(
        field_type="GeometryNodeInputMaterial",
        output_socket="Material",
        properties={"material": ("MATERIAL", material)} if material else {},
        label="input_material",
    )


# ---------------------------------------------------------------------------
# Scene / environment
# ---------------------------------------------------------------------------


def scene_time(output: str = "Seconds") -> IRFieldInput:
    """Current scene animation time.

    *output*: ``"Seconds"`` or ``"Frame"``.
    """
    return IRFieldInput(
        field_type="GeometryNodeInputSceneTime",
        output_socket=output,
        label="scene_time",
    )


def active_camera() -> IRFieldInput:
    """The scene's active camera object."""
    return IRFieldInput(
        field_type="GeometryNodeInputActiveCamera",
        output_socket="Active Camera",
        label="active_camera",
    )


def self_object() -> IRFieldInput:
    """The object that owns the current geometry nodes modifier."""
    return IRFieldInput(
        field_type="GeometryNodeSelfObject",
        output_socket="Self Object",
        label="self_object",
    )


def is_viewport() -> IRFieldInput:
    """Whether nodes are evaluated for the viewport (not final render)."""
    return IRFieldInput(
        field_type="GeometryNodeIsViewport",
        output_socket="Is Viewport",
        label="is_viewport",
    )


# ---------------------------------------------------------------------------
# Instance info
# ---------------------------------------------------------------------------


def instance_bounds(
    use_radius: bool = True,
    output: str = "Min",
) -> IRFieldInput:
    """Bounding box of each instance's geometry.

    *output*: ``"Min"`` or ``"Max"`` (vector).
    """
    return IRFieldInput(
        field_type="GeometryNodeInputInstanceBounds",
        output_socket=output,
        input_defaults={"Use Radius": use_radius},
        label="instance_bounds",
    )


# ---------------------------------------------------------------------------
# Grease Pencil / Named Layer
# ---------------------------------------------------------------------------


def named_layer_selection(name: str = "") -> IRFieldInput:
    """Selection of a Grease Pencil layer by name."""
    return IRFieldInput(
        field_type="GeometryNodeInputNamedLayerSelection",
        output_socket="Selection",
        input_defaults={"Name": name},
        label="named_layer_selection",
    )


# ---------------------------------------------------------------------------
# Mesh — Face Group Boundaries
# ---------------------------------------------------------------------------


def face_group_boundaries(face_group_id: int = 0) -> IRFieldInput:
    """Edges on boundaries between face groups with the same ID.

    *face_group_id*: default face set value.
    """
    return IRFieldInput(
        field_type="GeometryNodeMeshFaceSetBoundaries",
        output_socket="Boundary Edges",
        input_defaults={"Face Set": face_group_id},
        label="face_group_boundaries",
    )


# ---------------------------------------------------------------------------
# Mesh topology — corner queries
# ---------------------------------------------------------------------------


def corners_of_edge(
    edge_index: int = 0,
    weights: float = 0.0,
    sort_index: int = 0,
    output: str = "Corner Index",
) -> IRFieldInput:
    """Face corners connected to an edge.

    *output*: ``"Corner Index"`` or ``"Total"``.
    """
    return IRFieldInput(
        field_type="GeometryNodeCornersOfEdge",
        output_socket=output,
        input_defaults={
            "Edge Index": edge_index,
            "Weights": weights,
            "Sort Index": sort_index,
        },
        label="corners_of_edge",
    )


def corners_of_face(
    face_index: int = 0,
    weights: float = 0.0,
    sort_index: int = 0,
    output: str = "Corner Index",
) -> IRFieldInput:
    """Corners that make up a face.

    *output*: ``"Corner Index"`` or ``"Total"``.
    """
    return IRFieldInput(
        field_type="GeometryNodeCornersOfFace",
        output_socket=output,
        input_defaults={
            "Face Index": face_index,
            "Weights": weights,
            "Sort Index": sort_index,
        },
        label="corners_of_face",
    )


def corners_of_vertex(
    vertex_index: int = 0,
    weights: float = 0.0,
    sort_index: int = 0,
    output: str = "Corner Index",
) -> IRFieldInput:
    """Face corners connected to a vertex.

    *output*: ``"Corner Index"`` or ``"Total"``.
    """
    return IRFieldInput(
        field_type="GeometryNodeCornersOfVertex",
        output_socket=output,
        input_defaults={
            "Vertex Index": vertex_index,
            "Weights": weights,
            "Sort Index": sort_index,
        },
        label="corners_of_vertex",
    )


def edges_of_corner(
    corner_index: int = 0,
    output: str = "Next Edge Index",
) -> IRFieldInput:
    """Edges on both sides of a face corner.

    *output*: ``"Next Edge Index"`` or ``"Previous Edge Index"``.
    """
    return IRFieldInput(
        field_type="GeometryNodeEdgesOfCorner",
        output_socket=output,
        input_defaults={"Corner Index": corner_index},
        label="edges_of_corner",
    )


def edges_of_vertex(
    vertex_index: int = 0,
    weights: float = 0.0,
    sort_index: int = 0,
    output: str = "Edge Index",
) -> IRFieldInput:
    """Edges connected to a vertex.

    *output*: ``"Edge Index"`` or ``"Total"``.
    """
    return IRFieldInput(
        field_type="GeometryNodeEdgesOfVertex",
        output_socket=output,
        input_defaults={
            "Vertex Index": vertex_index,
            "Weights": weights,
            "Sort Index": sort_index,
        },
        label="edges_of_vertex",
    )


def face_of_corner(
    corner_index: int = 0,
    output: str = "Face Index",
) -> IRFieldInput:
    """Face that a corner belongs to.

    *output*: ``"Face Index"`` or ``"Index in Face"``.
    """
    return IRFieldInput(
        field_type="GeometryNodeFaceOfCorner",
        output_socket=output,
        input_defaults={"Corner Index": corner_index},
        label="face_of_corner",
    )


def vertex_of_corner(corner_index: int = 0) -> IRFieldInput:
    """Vertex that a face corner is attached to."""
    return IRFieldInput(
        field_type="GeometryNodeVertexOfCorner",
        output_socket="Vertex Index",
        input_defaults={"Corner Index": corner_index},
        label="vertex_of_corner",
    )


def offset_corner_in_face(
    corner_index: int = 0,
    offset: int = 0,
) -> IRFieldInput:
    """Offset a corner index within the same face."""
    return IRFieldInput(
        field_type="GeometryNodeOffsetCornerInFace",
        output_socket="Corner Index",
        input_defaults={"Corner Index": corner_index, "Offset": offset},
        label="offset_corner_in_face",
    )


# ---------------------------------------------------------------------------
# Index of Nearest
# ---------------------------------------------------------------------------


def index_of_nearest(output: str = "Index") -> IRFieldInput:
    """Find the nearest element in a group.

    *output*: ``"Index"`` (int) or ``"Has Neighbor"`` (bool).
    """
    return IRFieldInput(
        field_type="GeometryNodeIndexOfNearest",
        output_socket=output,
        label="index_of_nearest",
    )


# ---------------------------------------------------------------------------
# Edge selection / grouping
# ---------------------------------------------------------------------------


def edge_paths_to_selection(
    start_vertices: bool = True,
    next_vertex_index: int = -1,
) -> IRFieldInput:
    """Selection of edges by following paths across mesh edges."""
    return IRFieldInput(
        field_type="GeometryNodeEdgePathsToSelection",
        output_socket="Selection",
        input_defaults={
            "Start Vertices": start_vertices,
            "Next Vertex Index": next_vertex_index,
        },
        label="edge_paths_to_selection",
    )


def edges_to_face_groups(boundary_edges: bool = True) -> IRFieldInput:
    """Group faces into regions surrounded by boundary edges."""
    return IRFieldInput(
        field_type="GeometryNodeEdgesToFaceGroups",
        output_socket="Face Group ID",
        input_defaults={"Boundary Edges": boundary_edges},
        label="edges_to_face_groups",
    )


# ---------------------------------------------------------------------------
# Batch 19 — Instance / Viewport / Tool / Reference / Stats / UV / Utility
# ---------------------------------------------------------------------------


def instance_transform() -> IRFieldInput:
    """Read the transform matrix of each instance."""
    return IRFieldInput(
        field_type="GeometryNodeInstanceTransform",
        output_socket="Transform",
        label="instance_transform",
    )


def viewport_transform(output: str = "Projection") -> IRFieldInput:
    """Read viewport camera matrices.

    *output*: ``"Projection"`` | ``"View"`` | ``"Is Orthographic"``
    """
    return IRFieldInput(
        field_type="GeometryNodeViewportTransform",
        output_socket=output,
        label="viewport_transform",
    )


def tool_selection(output: str = "Boolean") -> IRFieldInput:
    """Current tool selection field.

    *output*: ``"Boolean"`` | ``"Float"``
    """
    return IRFieldInput(
        field_type="GeometryNodeToolSelection",
        output_socket=output,
        label="tool_selection",
    )


def tool_face_set(output: str = "Face Set") -> IRFieldInput:
    """Active face-set value.

    *output*: ``"Face Set"`` | ``"Exists"``
    """
    return IRFieldInput(
        field_type="GeometryNodeToolFaceSet",
        output_socket=output,
        label="tool_face_set",
    )


def tool_mouse_position(output: str = "Mouse X") -> IRFieldInput:
    """Mouse position in viewport pixels.

    *output*: ``"Mouse X"`` | ``"Mouse Y"`` | ``"Region Width"`` | ``"Region Height"``
    """
    return IRFieldInput(
        field_type="GeometryNodeToolMousePosition",
        output_socket=output,
        label="tool_mouse_position",
    )


def tool_3d_cursor(output: str = "Location") -> IRFieldInput:
    """3-D cursor location / rotation.

    *output*: ``"Location"`` | ``"Rotation"``
    """
    return IRFieldInput(
        field_type="GeometryNodeTool3DCursor",
        output_socket=output,
        label="tool_3d_cursor",
    )


def tool_active_element(
    domain: str = "POINT", output: str = "Index",
) -> IRFieldInput:
    """Index of the active mesh element in the given *domain*.

    *domain*: ``"POINT"`` | ``"EDGE"`` | ``"FACE"``
    *output*: ``"Index"`` | ``"Exists"``
    """
    return IRFieldInput(
        field_type="GeometryNodeToolActiveElement",
        output_socket=output,
        properties={"domain": domain},
        label="tool_active_element",
    )


# --- Reference input nodes ---------------------------------------------------


def input_collection(collection: str = "") -> IRFieldInput:
    """Reference a Blender collection by name."""
    return IRFieldInput(
        field_type="GeometryNodeInputCollection",
        output_socket="Collection",
        properties={"collection": ("COLLECTION", collection)} if collection else {},
        label="input_collection",
    )


def input_image(image: str = "") -> IRFieldInput:
    """Reference a Blender image by name."""
    return IRFieldInput(
        field_type="GeometryNodeInputImage",
        output_socket="Image",
        properties={"image": ("IMAGE", image)} if image else {},
        label="input_image",
    )


def input_object(object_name: str = "") -> IRFieldInput:
    """Reference a Blender object by name."""
    return IRFieldInput(
        field_type="GeometryNodeInputObject",
        output_socket="Object",
        properties={"object": ("OBJECT", object_name)} if object_name else {},
        label="input_object",
    )


# --- Nodes with input sockets + properties -----------------------------------


def camera_info(
    camera: str = "", output: str = "Focal Length",
) -> IRFieldInput:
    """Camera information node.

    *camera*: object name; empty → no default (uses connected input).
    *output*: ``"Focal Length"`` | ``"Sensor"`` | ``"Shift"`` |
              ``"Clip Start"`` | ``"Clip End"`` | ``"Focus Distance"`` |
              ``"Is Orthographic"`` | ``"Orthographic Scale"`` | ``"Projection Matrix"``
    """
    defaults: dict = {}
    if camera:
        defaults["Camera"] = ("OBJECT", camera)
    return IRFieldInput(
        field_type="GeometryNodeCameraInfo",
        output_socket=output,
        input_defaults=defaults,
        label="camera_info",
    )


def image_texture(
    image: str = "",
    interpolation: str = "Linear",
    extension: str = "REPEAT",
    output: str = "Color",
) -> IRFieldInput:
    """Sample an image texture.

    *image*: image name for the Image input; empty → unset.
    *interpolation*: ``"Linear"`` | ``"Closest"`` | ``"Cubic"``
    *extension*: ``"REPEAT"`` | ``"EXTEND"`` | ``"CLIP"``
    *output*: ``"Color"`` | ``"Alpha"``
    """
    defaults: dict = {}
    if image:
        defaults["Image"] = ("IMAGE", image)
    return IRFieldInput(
        field_type="GeometryNodeImageTexture",
        output_socket=output,
        properties={"interpolation": interpolation, "extension": extension},
        input_defaults=defaults,
        label="image_texture",
    )


def image_info(image: str = "", frame: int = 0, output: str = "Width") -> IRFieldInput:
    """Query image metadata.

    *output*: ``"Width"`` | ``"Height"`` | ``"Has Alpha"`` | ``"Frame Count"`` | ``"FPS"``
    """
    defaults: dict = {"Frame": frame}
    if image:
        defaults["Image"] = ("IMAGE", image)
    return IRFieldInput(
        field_type="GeometryNodeImageInfo",
        output_socket=output,
        input_defaults=defaults,
        label="image_info",
    )


# --- Field statistics nodes ---------------------------------------------------


def field_average(
    group_id: int = 0,
    data_type: str = "FLOAT",
    domain: str = "POINT",
    output: str = "Mean",
) -> IRFieldInput:
    """Average of a field over elements.

    *output*: ``"Mean"`` | ``"Median"``
    """
    return IRFieldInput(
        field_type="GeometryNodeFieldAverage",
        output_socket=output,
        properties={"data_type": data_type, "domain": domain},
        input_defaults={"Group ID": group_id},
        label="field_average",
    )


def field_min_max(
    group_id: int = 0,
    data_type: str = "FLOAT",
    domain: str = "POINT",
    output: str = "Min",
) -> IRFieldInput:
    """Minimum and maximum of a field.

    *output*: ``"Min"`` | ``"Max"``
    """
    return IRFieldInput(
        field_type="GeometryNodeFieldMinAndMax",
        output_socket=output,
        properties={"data_type": data_type, "domain": domain},
        input_defaults={"Group ID": group_id},
        label="field_min_max",
    )


def field_variance(
    group_id: int = 0,
    data_type: str = "FLOAT",
    domain: str = "POINT",
    output: str = "Standard Deviation",
) -> IRFieldInput:
    """Standard deviation and variance of a field.

    *output*: ``"Standard Deviation"`` | ``"Variance"``
    """
    return IRFieldInput(
        field_type="GeometryNodeFieldVariance",
        output_socket=output,
        properties={"data_type": data_type, "domain": domain},
        input_defaults={"Group ID": group_id},
        label="field_variance",
    )


# --- UV nodes -----------------------------------------------------------------


def uv_pack_islands(
    margin: float = 0.001, rotate: bool = True,
) -> IRFieldInput:
    """Pack UV islands into the UV space."""
    return IRFieldInput(
        field_type="GeometryNodeUVPackIslands",
        output_socket="UV",
        input_defaults={"Margin": margin, "Rotate": rotate},
        label="uv_pack_islands",
    )


def uv_unwrap(
    margin: float = 0.001,
    fill_holes: bool = True,
    method: str = "ANGLE_BASED",
) -> IRFieldInput:
    """Unwrap mesh faces to UV coordinates.

    *method*: ``"ANGLE_BASED"`` | ``"CONFORMAL"``
    """
    return IRFieldInput(
        field_type="GeometryNodeUVUnwrap",
        output_socket="UV",
        properties={"method": method},
        input_defaults={"Margin": margin, "Fill Holes": fill_holes},
        label="uv_unwrap",
    )


# --- String / utility nodes ---------------------------------------------------


def join_strings(delimiter: str = "") -> IRFieldInput:
    """Concatenate strings with a delimiter."""
    return IRFieldInput(
        field_type="GeometryNodeStringJoin",
        output_socket="String",
        input_defaults={"Delimiter": delimiter},
        label="join_strings",
    )


def import_text(path: str = "") -> IRFieldInput:
    """Import text from a file path."""
    return IRFieldInput(
        field_type="GeometryNodeImportText",
        output_socket="String",
        input_defaults={"Path": path},
        label="import_text",
    )


# --- Batch 20 — field processors, grid, gizmo, warning ------------------------


def blur_attribute(
    value: float = 0.0,
    iterations: int = 1,
    weight: float = 1.0,
    data_type: str = "FLOAT",
) -> IRFieldInput:
    """Smooth an attribute value with neighboring values."""
    return IRFieldInput(
        field_type="GeometryNodeBlurAttribute",
        output_socket="Value",
        properties={"data_type": data_type},
        input_defaults={"Value": value, "Iterations": iterations, "Weight": weight},
        label="blur_attribute",
    )


def accumulate_field(
    value: float = 1.0,
    group_id: int = 0,
    data_type: str = "FLOAT",
    domain: str = "POINT",
    output: str = "Leading",
) -> IRFieldInput:
    """Running accumulation of a field value.

    *output*: ``"Leading"`` | ``"Trailing"`` | ``"Total"``
    """
    return IRFieldInput(
        field_type="GeometryNodeAccumulateField",
        output_socket=output,
        properties={"data_type": data_type, "domain": domain},
        input_defaults={"Value": value, "Group Index": group_id},
        label="accumulate_field",
    )


def evaluate_at_index(
    value: float = 0.0,
    index: int = 0,
    domain: str = "POINT",
    data_type: str = "FLOAT",
) -> IRFieldInput:
    """Retrieve a field value at a specific index."""
    return IRFieldInput(
        field_type="GeometryNodeFieldAtIndex",
        output_socket="Value",
        properties={"domain": domain, "data_type": data_type},
        input_defaults={"Value": value, "Index": index},
        label="evaluate_at_index",
    )


def evaluate_on_domain(
    value: float = 0.0,
    domain: str = "POINT",
    data_type: str = "FLOAT",
) -> IRFieldInput:
    """Evaluate a field on a different domain."""
    return IRFieldInput(
        field_type="GeometryNodeFieldOnDomain",
        output_socket="Value",
        properties={"domain": domain, "data_type": data_type},
        input_defaults={"Value": value},
        label="evaluate_on_domain",
    )


def grid_info(
    data_type: str = "FLOAT",
    output: str = "Transform",
) -> IRFieldInput:
    """Query information about a volume grid.

    *output*: ``"Transform"`` | ``"Background Value"``
    """
    return IRFieldInput(
        field_type="GeometryNodeGridInfo",
        output_socket=output,
        properties={"data_type": data_type},
        label="grid_info",
    )


def sample_grid(
    data_type: str = "FLOAT",
    interpolation_mode: str = "TRILINEAR",
) -> IRFieldInput:
    """Sample a volume grid at a position.

    *interpolation_mode*: ``"NEAREST"`` | ``"TRILINEAR"`` | ``"TRIQUADRATIC"``
    """
    return IRFieldInput(
        field_type="GeometryNodeSampleGrid",
        output_socket="Value",
        properties={"data_type": data_type, "interpolation_mode": interpolation_mode},
        label="sample_grid",
    )


def sample_grid_index(
    x: int = 0, y: int = 0, z: int = 0,
    data_type: str = "FLOAT",
) -> IRFieldInput:
    """Sample a volume grid at a specific voxel index."""
    return IRFieldInput(
        field_type="GeometryNodeSampleGridIndex",
        output_socket="Value",
        properties={"data_type": data_type},
        input_defaults={"X": x, "Y": y, "Z": z},
        label="sample_grid_index",
    )


def sdf_grid_boolean(
    operation: str = "DIFFERENCE",
) -> IRFieldInput:
    """Perform a boolean operation on two SDF grids.

    *operation*: ``"INTERSECT"`` | ``"UNION"`` | ``"DIFFERENCE"``
    """
    return IRFieldInput(
        field_type="GeometryNodeSDFGridBoolean",
        output_socket="Grid",
        properties={"operation": operation},
        label="sdf_grid_boolean",
    )


def warning_node(
    show: bool = True,
    message: str = "",
    warning_type: str = "ERROR",
) -> IRFieldInput:
    """Emit a warning or error message.

    *warning_type*: ``"ERROR"`` | ``"WARNING"`` | ``"INFO"``
    """
    return IRFieldInput(
        field_type="GeometryNodeWarning",
        output_socket="Show",
        properties={"warning_type": warning_type},
        input_defaults={"Show": show, "Message": message},
        label="warning",
    )


def gizmo_dial(
    value: float = 0.0,
    position: tuple[float, float, float] = (0.0, 0.0, 0.0),
    up: tuple[float, float, float] = (0.0, 0.0, 1.0),
    screen_space: bool = True,
    radius: float = 1.0,
    color_id: str = "PRIMARY",
) -> IRFieldInput:
    """Create a dial gizmo for angular input.

    *color_id*: ``"PRIMARY"`` | ``"SECONDARY"`` | ``"X"`` | ``"Y"`` | ``"Z"``
    """
    return IRFieldInput(
        field_type="GeometryNodeGizmoDial",
        output_socket="Transform",
        properties={"color_id": color_id},
        input_defaults={
            "Value": value, "Position": position, "Up": up,
            "Screen Space": screen_space, "Radius": radius,
        },
        label="gizmo_dial",
    )


def gizmo_linear(
    value: float = 0.0,
    position: tuple[float, float, float] = (0.0, 0.0, 0.0),
    direction: tuple[float, float, float] = (0.0, 0.0, 1.0),
    color_id: str = "PRIMARY",
    draw_style: str = "ARROW",
) -> IRFieldInput:
    """Create a linear gizmo for sliding input.

    *color_id*: ``"PRIMARY"`` | ``"SECONDARY"`` | ``"X"`` | ``"Y"`` | ``"Z"``

    *draw_style*: ``"ARROW"`` | ``"CROSS"`` | ``"BOX"``
    """
    return IRFieldInput(
        field_type="GeometryNodeGizmoLinear",
        output_socket="Transform",
        properties={"color_id": color_id, "draw_style": draw_style},
        input_defaults={
            "Value": value, "Position": position, "Direction": direction,
        },
        label="gizmo_linear",
    )


def gizmo_transform(
    position: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    use_translation_x: bool = False,
    use_translation_y: bool = False,
    use_translation_z: bool = False,
    use_rotation_x: bool = False,
    use_rotation_y: bool = False,
    use_rotation_z: bool = False,
    use_scale_x: bool = False,
    use_scale_y: bool = False,
    use_scale_z: bool = False,
) -> IRFieldInput:
    """Create a full transform gizmo."""
    return IRFieldInput(
        field_type="GeometryNodeGizmoTransform",
        output_socket="Transform",
        properties={
            "use_translation_x": use_translation_x,
            "use_translation_y": use_translation_y,
            "use_translation_z": use_translation_z,
            "use_rotation_x": use_rotation_x,
            "use_rotation_y": use_rotation_y,
            "use_rotation_z": use_rotation_z,
            "use_scale_x": use_scale_x,
            "use_scale_y": use_scale_y,
            "use_scale_z": use_scale_z,
        },
        input_defaults={
            "Position": position, "Rotation": rotation,
        },
        label="gizmo_transform",
    )
