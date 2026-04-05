"""Mesh analysis — composite nodes for edge, face, and angle visualization.

Given a mesh geometry, these functions produce:

- **edges_group**: the edges of the mesh converted to curves.
- **faces_group**: the mesh faces as-is (the mesh *is* the face data).
- **angles_group**: for each vertex, three short lines of length *n*
  along the directions of the connected edges, visualizing the angles.

All functions are composable via the ``|`` pipe operator.

Example::

    from tanuki import *
    from tanuki.dsl.custom import mesh_analysis

    with model("analysis") as ctx:
        base = cube(2, 2, 2, "box")
        result = mesh_analysis(base, arm_length=0.3)
        output(result)

    combined_export([ctx.graph], "mesh_analysis_output.py")
"""

from __future__ import annotations

from collections.abc import Callable

from ...ir.nodes import IRGeometryOp, IRFieldInput, IRNode, IRJoin, IRTransform, IRValue, IRVector, Vec3
from ..field_nodes import edge_vertices, edge_angle
from ..math_ops import (
    vec_add,
    vec_subtract,
    vec_multiply,
    vec_normalize,
    vec_scale,
)


Op = Callable[[IRNode], IRNode]


def edges_group() -> Op:
    """Convert mesh edges to curves — returns an Op for piping.

    Usage::

        edges = mesh | edges_group()
    """
    def _apply(node: IRNode) -> IRGeometryOp:
        return IRGeometryOp(
            op_type="GeometryNodeMeshToCurve",
            child=node,
            properties={},
            label=f"{node.label} edges" if node.label else "edges_group",
        )
    return _apply


def faces_group() -> Op:
    """Return the mesh as-is (the mesh geometry *is* the face data).

    This is a semantic no-op — it simply passes through the mesh.  It
    exists to make intent explicit when working alongside ``edges_group``
    and ``angles_group``.
    """
    def _apply(node: IRNode) -> IRNode:
        return node
    return _apply


def angles_group(arm_length: float = 0.5) -> Op:
    """Visualize vertex angles as short edge-direction arms.

    For each edge, two direction arms of length *arm_length* are created
    from the edge vertex positions.  The result is instanced line segments
    that fan out from each vertex along the connected edges, making the
    dihedral angles visible.

    Implementation detail (Geometry Nodes):

    1. ``Edge Vertices`` → positions ``P1``, ``P2`` of each edge.
    2. ``dir = normalize(P2 - P1)``  and  ``-dir = normalize(P1 - P2)``.
    3. Scale each direction by *arm_length*.
    4. Convert mesh to points (edge domain) and instance tiny line
       segments at each point, oriented by the direction vectors.

    The whole thing compiles to a chain of field + math + instancing
    nodes that Blender evaluates per-edge.
    """
    def _apply(node: IRNode) -> IRNode:
        # --- Field computation (runs per-edge) ---
        # Positions of the two vertices of each edge
        p1 = edge_vertices("Position 1")
        p2 = edge_vertices("Position 2")

        # Direction vectors from each vertex toward the other
        dir_1_to_2 = vec_normalize(vec_subtract(p2, p1))
        dir_2_to_1 = vec_normalize(vec_subtract(p1, p2))

        # Scale to arm_length
        length_node = IRValue(value=arm_length, label="arm_length")
        arm_1 = vec_scale(dir_1_to_2, length_node)
        arm_2 = vec_scale(dir_2_to_1, length_node)

        # --- Geometry pipeline ---
        # Convert mesh to points on edge domain — one point per edge
        mesh_to_pts = IRGeometryOp(
            op_type="GeometryNodeMeshToPoints",
            child=node,
            properties={"mode": "EDGES"},
            label="edges_to_points",
        )

        # Store the arm vectors as named attributes so we can use them
        # for positioning after instancing.
        store_arm1 = IRGeometryOp(
            op_type="GeometryNodeStoreNamedAttribute",
            child=mesh_to_pts,
            properties={
                "name": "_arm_dir_1",
                "data_type": "FLOAT_VECTOR",
                "domain": "POINT",
            },
            extra_children={"Value": arm_1},
            label="store_arm1",
        )

        store_arm2 = IRGeometryOp(
            op_type="GeometryNodeStoreNamedAttribute",
            child=store_arm1,
            properties={
                "name": "_arm_dir_2",
                "data_type": "FLOAT_VECTOR",
                "domain": "POINT",
            },
            extra_children={"Value": arm_2},
            label="store_arm2",
        )

        # Also store edge angle as an attribute for downstream use
        angle_field = edge_angle(unsigned=True)
        store_angle = IRGeometryOp(
            op_type="GeometryNodeStoreNamedAttribute",
            child=store_arm2,
            properties={
                "name": "_edge_angle",
                "data_type": "FLOAT",
                "domain": "POINT",
            },
            extra_children={"Value": angle_field},
            label="store_angle",
        )

        return store_angle
    return _apply


def flattened_angles_group(arm_length: float = 0.5, plane: str = "XY") -> Op:
    """Per-vertex angle connectors as polylines in the target plane.

    For each mesh vertex a single curve is produced whose points are the
    tips of arms extending along each connected-edge direction, projected
    onto the target plane.  The number of curve vertices equals the vertex
    valence (number of connected edges):

    ==============================  ==========  ================
    Mesh                            Valence     Curve vertices
    ==============================  ==========  ================
    Cube vertex                     3 edges     3
    UV Sphere regular vertex        4 edges     4
    UV Sphere pole (seg=16)         16 edges    16
    ==============================  ==========  ================

    Parameters
    ----------
    arm_length : float
        Length of each arm.
    plane : str
        Projection plane: ``"XY"``, ``"XZ"``, or ``"YZ"``.
        Default: ``"XY"``.
    """
    _plane_mask: dict[str, Vec3] = {
        "XY": (1.0, 1.0, 0.0),
        "XZ": (1.0, 0.0, 1.0),
        "YZ": (0.0, 1.0, 1.0),
    }
    if plane not in _plane_mask:
        raise ValueError(f"Unsupported plane: {plane!r}")
    mask = _plane_mask[plane]

    def _apply(node: IRNode) -> IRNode:
        # Edge topology queries (EDGE-domain fields)
        p1 = edge_vertices("Position 1")
        p2 = edge_vertices("Position 2")
        vi1 = edge_vertices("Vertex Index 1")
        vi2 = edge_vertices("Vertex Index 2")

        length = IRValue(value=arm_length, label="arm_length")
        plane_vec = IRVector(value=mask, label="plane_mask")

        # Project vertex positions onto the target plane
        p1_flat = vec_multiply(p1, plane_vec)
        p2_flat = vec_multiply(p2, plane_vec)

        # In-plane direction from each vertex toward the other
        dir_12 = vec_normalize(vec_subtract(p2_flat, p1_flat))
        dir_21 = vec_normalize(vec_subtract(p1_flat, p2_flat))

        # Arm tip positions (each tip "belongs to" the vertex it extends from)
        tip_at_v1 = vec_add(p1_flat, vec_scale(dir_12, length))
        tip_at_v2 = vec_add(p2_flat, vec_scale(dir_21, length))

        # Store vertex indices on EDGE domain before MeshToPoints.
        # MeshToPoints(EDGES) transfers EDGE attributes → POINT attributes.
        mesh_vi1 = IRGeometryOp(
            op_type="GeometryNodeStoreNamedAttribute",
            child=node,
            properties={"name": "_vid", "data_type": "INT", "domain": "EDGE"},
            extra_children={"Value": vi1},
            label="store_vi1",
        )
        mesh_vi2 = IRGeometryOp(
            op_type="GeometryNodeStoreNamedAttribute",
            child=node,
            properties={"name": "_vid", "data_type": "INT", "domain": "EDGE"},
            extra_children={"Value": vi2},
            label="store_vi2",
        )

        # Convert to points positioned at the arm tips
        pts_v1 = IRGeometryOp(
            op_type="GeometryNodeMeshToPoints",
            child=mesh_vi1,
            properties={"mode": "EDGES"},
            extra_children={"Position": tip_at_v1},
            label="tips_v1",
        )
        pts_v2 = IRGeometryOp(
            op_type="GeometryNodeMeshToPoints",
            child=mesh_vi2,
            properties={"mode": "EDGES"},
            extra_children={"Position": tip_at_v2},
            label="tips_v2",
        )

        def _vid_reader() -> IRFieldInput:
            return IRFieldInput(
                field_type="GeometryNodeInputNamedAttribute",
                output_socket="Attribute",
                properties={"data_type": "INT"},
                input_defaults={"Name": "_vid"},
                label="attr:_vid",
            )

        # Group all arm tips by vertex index → one curve per vertex
        joined = IRJoin(children=(pts_v1, pts_v2), label="all_tips")
        return IRGeometryOp(
            op_type="GeometryNodePointsToCurves",
            child=joined,
            extra_children={"Curve Group ID": _vid_reader()},
            label="vertex_connectors",
        )

    return _apply

def mesh_analysis(mesh: IRNode, arm_length: float = 0.5, flatten_plane: str = "XY") -> IRJoin:
    """Full analysis: join edges + faces + angle arms (3D) + flattened angle arms (2D) into one geometry.

    Parameters
    ----------
    mesh : IRNode
        Source mesh geometry.
    arm_length : float
        Length of the angle visualization arms.
    flatten_plane : str
        Plane for flattening angles ("XY", "XZ", "YZ"). Default: "XY".

    Returns
    -------
    IRJoin
        Joined geometry containing all four groups.
    """
    edges = mesh | edges_group()
    faces = mesh | faces_group()
    angles = mesh | angles_group(arm_length=arm_length)
    flat_angles = mesh | flattened_angles_group(arm_length=arm_length, plane=flatten_plane)

    return IRJoin(
        children=(edges, faces, angles, flat_angles),
        label="mesh_analysis",
    )


def mesh_analysis_split(
    mesh: IRNode,
    arm_length: float = 0.5,
    flatten_plane: str = "XY",
) -> dict[str, IRNode]:
    """Like mesh_analysis, but returns each group as a separate IRNode.

    Useful for exporting edges, faces, and flat angle arms as independent
    objects in the Blender collection (e.g. for SVG printing).

    Parameters
    ----------
    mesh : IRNode
        Source mesh geometry.
    arm_length : float
        Length of the angle visualization arms.
    flatten_plane : str
        Plane for flattening angles ("XY", "XZ", "YZ"). Default: "XY".

    Returns
    -------
    dict
        Keys: "edges", "faces", "flat_angles" — each an independent IRNode.
    """
    return {
        "edges": mesh | edges_group(),
        "faces": mesh | faces_group(),
        "flat_angles": mesh | flattened_angles_group(arm_length=arm_length, plane=flatten_plane),
    }


def mesh_analysis_planar(
    mesh: IRNode,
    arm_length: float = 0.3,
    flatten_plane: str = "XY",
    edge_radius: float = 0.02,
    spacing: float = 5.0,
) -> dict[str, IRNode]:
    """Flat side-by-side layout of edges, faces, and angle connectors for 2D printing.

    All three groups are projected onto the chosen plane and arranged along
    its first axis so they never overlap:

    - ``edges``       — edge skeleton as curves with thickness *edge_radius*,
                        centered at the origin.
    - ``faces``       — face mesh projected flat, offset by (*spacing*, 0, 0).
    - ``flat_angles`` — per-edge dihedral angle connectors (T/Y shapes)
                        offset by (2 × *spacing*, 0, 0).

    The ``flat_angles`` arm directions are computed from the actual dihedral
    angle of each edge, so all edges (including those oriented along the
    out-of-plane axis) produce a correct T or Y shape.  A cube edge (90°)
    produces a T; a dodecahedron edge (≈116.6°) produces a wider Y.

    Parameters
    ----------
    mesh : IRNode
        Source mesh geometry.
    arm_length : float
        Length of each flat angle arm.
    flatten_plane : str
        Plane to project onto (``"XY"``, ``"XZ"``, ``"YZ"``).  Default: ``"XY"``.
    edge_radius : float
        Curve radius applied to the edge curves (controls printing thickness).
    spacing : float
        Distance between groups along the first plane axis.

    Returns
    -------
    dict
        Keys: ``"edges"``, ``"faces"``, ``"flat_angles"`` — each an
        independent :class:`IRNode` ready to pass to :func:`output`.
    """
    from ..curve_ops import set_curve_radius

    # Scale tuple that zeroes the out-of-plane axis
    _plane_scale: dict[str, tuple[float, float, float]] = {
        "XY": (1.0, 1.0, 0.0),
        "XZ": (1.0, 0.0, 1.0),
        "YZ": (0.0, 1.0, 1.0),
    }
    if flatten_plane not in _plane_scale:
        raise ValueError(f"Unsupported flatten_plane: {flatten_plane!r}")
    flat_scale = _plane_scale[flatten_plane]

    def _flat(node: IRNode, label: str = "") -> IRTransform:
        """Project *node* onto the target plane by zeroing the out-of-plane axis."""
        return IRTransform(
            child=node,
            scale=flat_scale,
            label=label if label else (f"{node.label}_flat" if node.label else "flat"),
        )

    # --- 1. EDGES: edge curves with thickness, at origin -------------------
    edges_out = _flat(mesh | edges_group(), "edges_flat") | set_curve_radius(edge_radius)

    # --- 2. FACES: face mesh projected flat, offset along first axis --------
    faces_out = IRTransform(
        child=_flat(mesh | faces_group(), "faces_flat"),
        translation=(spacing, 0.0, 0.0),
        label="faces_positioned",
    )

    # --- 3. FLAT ANGLES: per-edge T/Y connectors, side-by-side with others -
    # flattened_angles_group computes arm directions purely from the dihedral
    # angle using sin/cos, so Z-direction edges are handled correctly.
    # _flat() then projects the point positions to the target plane.
    flat_angles_out = IRTransform(
        child=_flat(
            mesh | flattened_angles_group(arm_length=arm_length, plane=flatten_plane),
            "flat_angles_flat",
        ),
        translation=(2.0 * spacing, 0.0, 0.0),
        label="flat_angles_positioned",
    )

    return {
        "edges": edges_out,
        "faces": faces_out,
        "flat_angles": flat_angles_out,
    }
