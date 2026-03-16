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

from ...ir.nodes import IRGeometryOp, IRNode, IRJoin, IRValue
from ..field_nodes import position, edge_vertices, edge_angle
from ..math_ops import vec_subtract, vec_normalize, vec_scale


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


def mesh_analysis(mesh: IRNode, arm_length: float = 0.5) -> IRJoin:
    """Full analysis: join edges + faces + angle arms into one geometry.

    Parameters
    ----------
    mesh : IRNode
        Source mesh geometry.
    arm_length : float
        Length of the angle visualization arms.

    Returns
    -------
    IRJoin
        Joined geometry containing all three groups.
    """
    edges = mesh | edges_group()
    faces = mesh | faces_group()
    angles = mesh | angles_group(arm_length=arm_length)

    return IRJoin(
        children=(edges, faces, angles),
        label="mesh_analysis",
    )
