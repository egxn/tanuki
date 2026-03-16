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
