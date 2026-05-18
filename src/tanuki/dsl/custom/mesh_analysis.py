"""Mesh analysis — composite nodes for edge, face, and angle visualization.

Given a mesh geometry, these functions produce:

- **edges_group**: the edges of the mesh converted to curves.
- **faces_group**: the mesh faces as-is (the mesh *is* the face data).
- **angles_group**: for each edge, a short 3-point connector curve in 3D.
- **flattened_angles_group**: for each edge, a planar 3-point connector
    curve whose opening angle matches the mesh dihedral angle.

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
from ..field_nodes import edge_angle, edge_vertices, index
from ..math_ops import (
    math_cos,
    math_multiply,
    math_subtract,
    math_sin,
    vec_add,
    vec_multiply,
    vec_normalize,
    vec_scale,
    vec_subtract,
)


Op = Callable[[IRNode], IRNode]


def _named_attribute_reader(name: str, data_type: str = "FLOAT") -> IRFieldInput:
    return IRFieldInput(
        field_type="GeometryNodeInputNamedAttribute",
        output_socket="Attribute",
        properties={"data_type": data_type},
        input_defaults={"Name": name},
        label=f"attr:{name}",
    )


def _edge_midpoint(p1: IRNode, p2: IRNode) -> IRNode:
    return vec_scale(vec_add(p1, p2), IRValue(value=0.5, label="half"))


def _ordered_edge_curves(
    node: IRNode,
    positions: tuple[IRNode, ...],
    *,
    label: str,
) -> IRGeometryOp:
    mesh_with_edge_id = IRGeometryOp(
        op_type="GeometryNodeStoreNamedAttribute",
        child=node,
        properties={"name": "_edge_id", "data_type": "INT", "domain": "EDGE"},
        extra_children={"Value": index()},
        label=f"{label}_edge_id",
    )

    point_sets: list[IRNode] = []
    for order, position in enumerate(positions):
        points = IRGeometryOp(
            op_type="GeometryNodeMeshToPoints",
            child=mesh_with_edge_id,
            properties={"mode": "EDGES"},
            extra_children={"Position": position},
            label=f"{label}_pt_{order}",
        )
        point_sets.append(
            IRGeometryOp(
                op_type="GeometryNodeStoreNamedAttribute",
                child=points,
                properties={
                    "name": "_point_order",
                    "data_type": "FLOAT",
                    "domain": "POINT",
                },
                extra_children={
                    "Value": IRValue(value=float(order), label=f"{label}_order_{order}"),
                },
                label=f"{label}_store_order_{order}",
            )
        )

    joined = IRJoin(children=tuple(point_sets), label=f"{label}_points")
    return IRGeometryOp(
        op_type="GeometryNodePointsToCurves",
        child=joined,
        extra_children={
            "Curve Group ID": _named_attribute_reader("_edge_id", data_type="INT"),
            "Weight": _named_attribute_reader("_point_order"),
        },
        label=label,
    )


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
    """Visualize each edge with a short 3-point connector curve.

    For each edge, this creates a polyline with three ordered points:

    1. A tip offset from vertex 1 toward vertex 2 by *arm_length*.
    2. The edge midpoint.
    3. A tip offset from vertex 2 toward vertex 1 by *arm_length*.

    The result is visible curve geometry rather than point attributes,
    so it can be joined directly with the mesh faces and edge curves.
    """
    def _apply(node: IRNode) -> IRNode:
        p1 = edge_vertices("Position 1")
        p2 = edge_vertices("Position 2")
        dir_1_to_2 = vec_normalize(vec_subtract(p2, p1))
        dir_2_to_1 = vec_normalize(vec_subtract(p1, p2))
        length_node = IRValue(value=arm_length, label="arm_length")
        tip_1 = vec_add(p1, vec_scale(dir_1_to_2, length_node))
        tip_2 = vec_add(p2, vec_scale(dir_2_to_1, length_node))
        midpoint = _edge_midpoint(p1, p2)

        return _ordered_edge_curves(
            node,
            (tip_1, midpoint, tip_2),
            label="edge_angle_arms",
        )
    return _apply


def flattened_angles_group(arm_length: float = 0.5, plane: str = "XY") -> Op:
    """Build one flat connector curve per edge in the target plane.

    Each edge becomes a 3-point polyline ``tip_a -> center -> tip_b``.
    The center is the edge midpoint projected to the target plane, while
    the two tips are laid out symmetrically in-plane using half the edge's
    interior dihedral angle. Blender's ``Edge Angle`` field yields the
    unsigned angle between adjacent face normals, so this helper converts
    it to the interior fold angle with ``pi - angle``. This keeps the
    planar connector valid even when the original edge is orthogonal to
    the target plane.

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
    if plane == "XY":
        primary_axis = IRVector(value=(1.0, 0.0, 0.0), label="plane_primary")
        secondary_axis = IRVector(value=(0.0, 1.0, 0.0), label="plane_secondary")
    elif plane == "XZ":
        primary_axis = IRVector(value=(1.0, 0.0, 0.0), label="plane_primary")
        secondary_axis = IRVector(value=(0.0, 0.0, 1.0), label="plane_secondary")
    else:
        primary_axis = IRVector(value=(0.0, 1.0, 0.0), label="plane_primary")
        secondary_axis = IRVector(value=(0.0, 0.0, 1.0), label="plane_secondary")

    def _apply(node: IRNode) -> IRNode:
        p1 = edge_vertices("Position 1")
        p2 = edge_vertices("Position 2")
        length = IRValue(value=arm_length, label="arm_length")
        plane_vec = IRVector(value=mask, label="plane_mask")
        midpoint = vec_multiply(_edge_midpoint(p1, p2), plane_vec)

        interior_angle = math_subtract(
            IRValue(value=3.141592653589793, label="pi"),
            edge_angle(unsigned=True),
        )
        half_angle = math_multiply(
            interior_angle,
            IRValue(value=0.5, label="half_angle_scale"),
        )
        cosine = math_cos(half_angle)
        sine = math_sin(half_angle)
        neg_sine = math_multiply(sine, IRValue(value=-1.0, label="neg_one"))

        dir_a = vec_add(
            vec_scale(primary_axis, cosine),
            vec_scale(secondary_axis, sine),
        )
        dir_b = vec_add(
            vec_scale(primary_axis, cosine),
            vec_scale(secondary_axis, neg_sine),
        )

        tip_a = vec_add(midpoint, vec_scale(dir_a, length))
        tip_b = vec_add(midpoint, vec_scale(dir_b, length))

        return _ordered_edge_curves(
            node,
            (tip_a, midpoint, tip_b),
            label="flat_edge_connectors",
        )

    return _apply

def mesh_analysis(mesh: IRNode, arm_length: float = 0.5, flatten_plane: str = "XY") -> IRJoin:
    """Full analysis: join edges, faces, 3D edge arms, and planar edge connectors.

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

    Useful for exporting edges, faces, 3D edge arms, and flat connectors
    as independent objects in the Blender collection.

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
        Keys: "edges", "faces", "angles", "flat_angles" — each an independent IRNode.
    """
    return {
        "edges": mesh | edges_group(),
        "faces": mesh | faces_group(),
        "angles": mesh | angles_group(arm_length=arm_length),
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
    - ``flat_angles`` — per-edge planar connector curves whose opening angle
                        matches the interior dihedral angle,
                        offset by (2 × *spacing*, 0, 0).

    The ``flat_angles`` arm directions are computed from the interior
    dihedral angle of each edge, so even edges orthogonal to the target
    plane still produce a valid planar connector.

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

    # --- 3. FLAT ANGLES: per-edge planar connectors, side-by-side ----------
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
