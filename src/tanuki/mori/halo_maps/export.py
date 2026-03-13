"""Halo CE — JMS v8200 exporter.

Exports a Blender mesh object to the Halo CE ``.jms`` (Joint Mesh Skeleton)
format used by the Halo Editing Kit. Run from inside Blender.

Coordinate transform: Blender is Z-up right-handed; Halo CE is Y-up.
Mapping: ``blender(x, y, z)`` → ``halo(x, -z, y)``

JMS v8200 section order
-----------------------
::

    <version>              # 8200
    <node_count>
    <node: name; parent; sibling; rot(i,j,k,w); pos(x,y,z)>...
    <material_count>
    <material: name; texture_path>...
    <marker_count>
    <marker: name; region; parent; rot; pos; radius>...
    <region_count>
    <region: name>...
    <vertex_count>
    <vertex: parent; pos(x,y,z); normal(x,y,z); uv_count; uv(u,v)>...
    <triangle_count>
    <triangle: region; material; v0; v1; v2>...
"""

from __future__ import annotations

import os

import bpy
import bmesh

__all__ = ["export_jms"]

# ---------------------------------------------------------------------------
# Coordinate transform helper
# ---------------------------------------------------------------------------

def _halo_xyz(x: float, y: float, z: float) -> tuple[float, float, float]:
    """Convert Blender world coord (Z-up) to Halo world coord (Y-up)."""
    return (x, -z, y)


def _halo_normal(x: float, y: float, z: float) -> tuple[float, float, float]:
    """Same rotation applied to direction vectors."""
    return _halo_xyz(x, y, z)


# ---------------------------------------------------------------------------
# Main exporter
# ---------------------------------------------------------------------------

def export_jms(
    obj_name: str,
    output_path: str,
    map_name: str = "unnamed",
) -> str:
    """Export a Blender mesh to JMS v8200 format.

    The mesh is **triangulated in a temporary bmesh copy** — the original
    object data is not modified.

    Parameters
    ----------
    obj_name:
        Name of the Blender mesh object to export.
    output_path:
        Filesystem path for the ``.jms`` file.  Parent directory must exist.
    map_name:
        Human-readable name embedded in a leading comment.  Defaults to
        ``"unnamed"``.

    Returns
    -------
    str
        The absolute path of the written file.

    Raises
    ------
    ValueError
        If *obj_name* is not found in the scene.
    TypeError
        If *obj_name* is not a Mesh object.
    """
    # ------------------------------------------------------------------
    # 1. Acquire object + evaluated mesh
    # ------------------------------------------------------------------
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        raise ValueError(f"Object {obj_name!r} not found in the scene.")
    if obj.type != 'MESH':
        raise TypeError(f"Object {obj_name!r} is not a Mesh (type={obj.type!r}).")

    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval  = obj.evaluated_get(depsgraph)
    mesh_eval = obj_eval.to_mesh()

    bm = bmesh.new()
    bm.from_mesh(mesh_eval)
    bmesh.ops.triangulate(bm, faces=bm.faces)

    uv_layer = bm.loops.layers.uv.active

    # ------------------------------------------------------------------
    # 2. Build vertex + triangle lists
    # ------------------------------------------------------------------
    verts = list(bm.verts)
    faces = list(bm.faces)

    # ------------------------------------------------------------------
    # 3. Format sections
    # ------------------------------------------------------------------
    lines: list[str] = []

    # -- header comment (not part of spec, helps with debugging) --------
    lines.append(f"; JMS v8200 — {map_name}")
    lines.append(f"; exported by tanuki.mori.halo_maps.export")

    # -- version ---------------------------------------------------------
    lines.append("8200")

    # -- nodes ------------------------------------------------------------
    # Minimal: 1 frame node with identity rotation and zero position.
    # JMS convention: quaternion (i, j, k, real)
    lines.append("1")          # node count
    lines.append("frame")      # name
    lines.append("-1")         # parent index  (-1 = root)
    lines.append("-1")         # first child
    lines.append("-1")         # sibling index
    lines.append("0.000000\t0.000000\t0.000000\t1.000000")  # rot i j k w
    lines.append("0.000000\t0.000000\t0.000000")            # pos x y z

    # -- materials --------------------------------------------------------
    lines.append("1")          # material count
    lines.append("+sky")       # name  (+sky = open sky in Halo CE)
    lines.append("<none>")     # texture path

    # -- markers ----------------------------------------------------------
    lines.append("0")          # marker count (none)

    # -- regions ----------------------------------------------------------
    lines.append("1")
    lines.append("unnamed")

    # -- vertices ---------------------------------------------------------
    lines.append(str(len(verts)))
    for v in verts:
        co    = v.co
        norm  = v.normal
        hx, hy, hz   = _halo_xyz(co.x, co.y, co.z)
        nx, ny, nz   = _halo_normal(norm.x, norm.y, norm.z)

        # Collect UVs from the first loop that owns this vertex
        uv_u, uv_v = 0.0, 0.0
        if uv_layer and v.link_loops:
            loop_uv = v.link_loops[0][uv_layer]
            uv_u = loop_uv.uv.x
            uv_v = loop_uv.uv.y

        lines.append("0")    # parent node index (frame = 0)
        lines.append(f"{hx:.6f}\t{hy:.6f}\t{hz:.6f}")
        lines.append(f"{nx:.6f}\t{ny:.6f}\t{nz:.6f}")
        lines.append("1")    # uv pair count
        lines.append(f"{uv_u:.6f}\t{uv_v:.6f}")

    # -- triangles --------------------------------------------------------
    lines.append(str(len(faces)))
    for f in faces:
        v_indices = [v.index for v in f.verts]
        if len(v_indices) != 3:
            # Should never happen after triangulate — defensive guard
            continue
        i0, i1, i2 = v_indices
        # region=0 (unnamed), material=0 (+sky)
        lines.append(f"0\t0\t{i0}\t{i1}\t{i2}")

    # ------------------------------------------------------------------
    # 4. Cleanup bmesh + temporary mesh
    # ------------------------------------------------------------------
    bm.free()
    obj_eval.to_mesh_clear()

    # ------------------------------------------------------------------
    # 5. Write file
    # ------------------------------------------------------------------
    output_path = os.path.abspath(output_path)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
        fh.write("\n")

    return output_path
