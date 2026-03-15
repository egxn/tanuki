"""Naranjos map — procedural building & border generator.

Reads *buildings.json* and *borders.json*, imports *map.svg* into Blender,
converts SVG paths to hollow multi-floor buildings in **Blam Units**
(1 BU ≈ 0.55 m), and places them in the ``BSP`` collection.

Run inside Blender::

    import importlib
    import tanuki.mori.halo_maps.naranjos.generate as ng
    importlib.reload(ng)
    ng.generate_naranjos()
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DIR = Path(__file__).resolve().parent

# 1 Blam Unit ≈ 0.55 metres
M_PER_BU = 0.55

# Wall thickness in BU  (~12 cm real → 0.12 / 0.55 ≈ 0.22 BU)
WALL_THICKNESS_BU = 0.22

# After Blender imports the SVG the coordinates end up in Blender's internal
# scale.  The raw imported dimensions for this map are approximately:
#     borders ≈ 40 394 × 38 560  Blender units (before scaling)
#
# To bring the campus footprint to a playable Halo CE size we apply this
# factor so the border perimeter lands around ~200 × 190 BU.
#
# ⚠  Tune this value if the XY footprint is too large or too small.
#    Quick calibration:
#       1. Run generate_naranjos()
#       2. Measure a building you know the real-world size of (metres)
#       3. expected_BU = real_metres / 0.55
#       4. Adjust SVG_TO_BU so that  measured_BU ≈ expected_BU
SVG_TO_BU = 0.005

# Curve resolution when converting SVG splines to mesh (segments per section).
# Higher = smoother but more polygons.
CURVE_RESOLUTION = 12


def m_to_bu(metres: float) -> float:
    """Convert real-world metres to Blam Units."""
    return metres / M_PER_BU


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_buildings() -> list[dict]:
    with open(_DIR / "buildings.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    for b in data:
        # Normalise the inconsistent key: "floors" vs "floor"
        if "floors" in b and "floor" not in b:
            b["floor"] = b["floors"]
        b.setdefault("floor", 1)
    return data


def _load_borders() -> dict:
    with open(_DIR / "borders.json", "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# SVG label → id mapping
# ---------------------------------------------------------------------------

_INK_NS = "http://www.inkscape.org/namespaces/inkscape"


def _parse_svg_label_map(svg_path: str | Path) -> dict[str, str]:
    """Parse *map.svg* and return ``{inkscape_label: svg_id}``.

    Blender names imported objects by the SVG ``id`` attribute, **not** by
    the ``inkscape:label``.  We need this mapping so we can look up a
    building's curve by its human-readable label.
    """
    tree = ET.parse(svg_path)
    label_to_id: dict[str, str] = {}
    for elem in tree.iter():
        label = elem.get(f"{{{_INK_NS}}}label")
        svg_id = elem.get("id")
        if label and svg_id:
            label_to_id[label.lower()] = svg_id
    return label_to_id


# ---------------------------------------------------------------------------
# SVG import helpers
# ---------------------------------------------------------------------------

def _import_svg() -> tuple[list[bpy.types.Object], dict[str, str]]:
    """Import *map.svg* and return (new_objects, label→id map)."""
    svg_path = _DIR / "map.svg"
    label_map = _parse_svg_label_map(svg_path)

    before = set(bpy.data.objects)
    bpy.ops.import_curve.svg(filepath=str(svg_path))
    after = set(bpy.data.objects)
    new_objs = list(after - before)

    if not new_objs:
        return new_objs, label_map

    # Apply SVG → BU scale and curve resolution
    for obj in new_objs:
        obj.scale = (SVG_TO_BU, SVG_TO_BU, SVG_TO_BU)
        if obj.type == "CURVE":
            obj.data.resolution_u = CURVE_RESOLUTION

    # Apply transforms so scale is baked into vertex coords
    bpy.ops.object.select_all(action="DESELECT")
    for obj in new_objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = new_objs[0]
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.select_all(action="DESELECT")

    return new_objs, label_map


def _find_curve(
    objects: list[bpy.types.Object],
    path_name: str,
    label_map: dict[str, str],
):
    """Find an imported SVG curve by *path_name* using the label→id map.

    1. Look up ``path_name`` in the SVG label→id map to get the SVG ``id``.
    2. Find the Blender curve object whose name matches that ``id``.
    3. Fall back to substring matching on the object name.
    """
    lower = path_name.lower()
    svg_id = label_map.get(lower)

    if svg_id:
        # Blender may append .001 etc — try prefix match
        for obj in objects:
            if obj.type == "CURVE" and obj.name.startswith(svg_id):
                return obj

    # Fallback: direct name match
    for obj in objects:
        if obj.type == "CURVE" and lower in obj.name.lower():
            return obj
    for obj in objects:
        if obj.type == "CURVE" and lower in obj.data.name.lower():
            return obj

    curves = [o.name for o in objects if o.type == "CURVE"]
    print(f"[naranjos] No match for '{path_name}' (svg_id={svg_id}). "
          f"Available: {curves}")
    return None


# ---------------------------------------------------------------------------
# Mesh generation helpers
# ---------------------------------------------------------------------------

def _curve_to_edge_mesh(curve_obj: bpy.types.Object) -> bpy.types.Object:
    """Duplicate a curve, ensure it is cyclic, and convert to an edge mesh."""
    bpy.ops.object.select_all(action="DESELECT")
    curve_obj.select_set(True)
    bpy.context.view_layer.objects.active = curve_obj
    bpy.ops.object.duplicate()
    dup = bpy.context.active_object

    # Make splines cyclic (closed)
    if dup.type == "CURVE":
        for spline in dup.data.splines:
            spline.use_cyclic_u = True

    # Convert curve → mesh
    bpy.ops.object.convert(target="MESH")

    # Remove any auto-generated faces, keeping only boundary edges
    mesh = dup.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    if bm.faces:
        bmesh.ops.delete(bm, geom=list(bm.faces), context="FACES_ONLY")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    return dup
    bpy.ops.object.convert(target="MESH")
    return dup


def _build_floor_module(
    footprint_obj: bpy.types.Object,
    floor_height_bu: float,
    wall_thickness_bu: float,
    z_offset: float,
) -> bpy.types.Object:
    """Build one sealed floor module (hollow box) from a footprint edge-loop.

    Steps
    -----
    1. Duplicate *footprint_obj* (flat edge-loop).
    2. Translate to *z_offset*.
    3. Fill edge-loop → floor polygon.
    4. Extrude face upward by *floor_height_bu* → solid prism.
    5. *Solidify* modifier (offset inward) → hollow room with thick walls,
       floor slab, and ceiling slab.
    """
    # ── duplicate footprint ───────────────────────────────────────────────
    bpy.ops.object.select_all(action="DESELECT")
    footprint_obj.select_set(True)
    bpy.context.view_layer.objects.active = footprint_obj
    bpy.ops.object.duplicate()
    module = bpy.context.active_object

    # ── move to z_offset ──────────────────────────────────────────────────
    module.location.z = z_offset
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

    # ── bmesh: fill → extrude ─────────────────────────────────────────────
    mesh = module.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    # Fill the edge-loop to create the floor face
    if bm.edges:
        bmesh.ops.contextual_create(bm, geom=list(bm.edges) + list(bm.verts))

        # Extrude floor face upward → solid prism
        faces = list(bm.faces)
        if faces:
            ret = bmesh.ops.extrude_face_region(bm, geom=faces)
            new_verts = [
                e for e in ret["geom"] if isinstance(e, bmesh.types.BMVert)
            ]
            bmesh.ops.translate(
                bm, verts=new_verts, vec=Vector((0, 0, floor_height_bu))
            )

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    # ── solidify → hollow room ────────────────────────────────────────────
    mod = module.modifiers.new("Solidify", "SOLIDIFY")
    mod.thickness = wall_thickness_bu
    mod.offset = -1.0        # grow inward
    mod.use_rim = True        # cap top/bottom rims
    mod.use_rim_only = False

    bpy.context.view_layer.objects.active = module
    bpy.ops.object.select_all(action="DESELECT")
    module.select_set(True)
    bpy.ops.object.modifier_apply(modifier="Solidify")

    return module


# ---------------------------------------------------------------------------
# Building & border generators
# ---------------------------------------------------------------------------

def _build_building(
    curve_obj: bpy.types.Object,
    building: dict,
) -> bpy.types.Object:
    """Generate a complete multi-floor building from a footprint curve."""
    name = building["name"]
    num_floors = building.get("floor", 1)
    floor_height_bu = m_to_bu(building.get("floor_height", 2.28))

    # Convert curve to a flat edge-mesh (the footprint)
    footprint = _curve_to_edge_mesh(curve_obj)

    # Build one sealed module per floor and collect them
    floor_modules: list[bpy.types.Object] = []
    for fi in range(num_floors):
        z_off = fi * floor_height_bu
        mod_obj = _build_floor_module(
            footprint, floor_height_bu, WALL_THICKNESS_BU, z_off
        )
        mod_obj.name = f"{name}_floor_{fi}"
        floor_modules.append(mod_obj)

    # Join all floor modules into a single object
    if len(floor_modules) > 1:
        bpy.ops.object.select_all(action="DESELECT")
        for m in floor_modules:
            m.select_set(True)
        bpy.context.view_layer.objects.active = floor_modules[0]
        bpy.ops.object.join()

    building_obj = bpy.context.active_object if len(floor_modules) > 1 else floor_modules[0]
    building_obj.name = name

    # Clean up the helper footprint mesh
    bpy.ops.object.select_all(action="DESELECT")
    footprint.select_set(True)
    bpy.context.view_layer.objects.active = footprint
    bpy.ops.object.delete()

    return building_obj


def _build_border(
    curve_obj: bpy.types.Object,
    border: dict,
) -> bpy.types.Object:
    """Generate border walls from a curve path."""
    name = border.get("name", "borders")
    height_bu = m_to_bu(float(border.get("height", 1.4)))

    # Convert to edge mesh
    edge_obj = _curve_to_edge_mesh(curve_obj)

    # bmesh: extrude edges upward (walls only, no floor fill)
    mesh = edge_obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    edges = list(bm.edges)
    if edges:
        ret = bmesh.ops.extrude_edge_only(bm, edges=edges)
        new_verts = [
            e for e in ret["geom"] if isinstance(e, bmesh.types.BMVert)
        ]
        bmesh.ops.translate(bm, verts=new_verts, vec=Vector((0, 0, height_bu)))

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    # Solidify for wall thickness + rim caps on top/bottom of wall
    mod = edge_obj.modifiers.new("Solidify", "SOLIDIFY")
    mod.thickness = WALL_THICKNESS_BU
    mod.offset = -1.0
    mod.use_rim = True
    mod.use_rim_only = False

    bpy.context.view_layer.objects.active = edge_obj
    bpy.ops.object.select_all(action="DESELECT")
    edge_obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier="Solidify")

    edge_obj.name = name
    return edge_obj


# ---------------------------------------------------------------------------
# Collection helpers
# ---------------------------------------------------------------------------

def _ensure_collection(name: str) -> bpy.types.Collection:
    if name not in bpy.data.collections:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return bpy.data.collections[name]


def _move_to_collection(obj: bpy.types.Object, coll_name: str) -> None:
    coll = _ensure_collection(coll_name)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

def _cleanup_svg_leftovers(svg_objects: list[bpy.types.Object]) -> None:
    """Remove original SVG curves and the auto-created SVG collection."""
    bpy.ops.object.select_all(action="DESELECT")
    for obj in svg_objects:
        if obj.name in bpy.data.objects:
            bpy.data.objects[obj.name].select_set(True)
    bpy.ops.object.delete()

    # The SVG importer creates a collection named after the file (e.g. "map")
    svg_stem = Path(_DIR / "map.svg").stem.lower()
    for coll in list(bpy.data.collections):
        if svg_stem in coll.name.lower() and len(coll.objects) == 0:
            bpy.data.collections.remove(coll)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_naranjos() -> None:
    """Generate all buildings and borders for the Naranjos map.

    1. Imports *map.svg* → curve objects.
    2. For each building in *buildings.json*: matches the SVG curve by
       ``path_name``, converts to a hollow multi-floor mesh, places in BSP.
    3. Generates border walls from *borders.json*.
    4. Cleans up SVG leftovers.

    All geometry is in **Blam Units** (1 BU ≈ 0.55 m).
    """
    buildings_data = _load_buildings()
    border_data = _load_borders()

    print("[naranjos] Importing map.svg …")
    svg_objects, label_map = _import_svg()

    if not svg_objects:
        print("[naranjos] ERROR: No objects imported from SVG.")
        return

    print(f"[naranjos] Imported {len(svg_objects)} SVG objects.")
    print(f"[naranjos] Label map: {label_map}")

    generated: list[bpy.types.Object] = []

    # ── buildings ─────────────────────────────────────────────────────────
    for bldg in buildings_data:
        path_name = bldg["path_name"]
        curve = _find_curve(svg_objects, path_name, label_map)
        if curve is None:
            print(f"[naranjos] WARNING: no curve for '{path_name}' — skipped.")
            continue

        floors = bldg.get("floor", 1)
        fh = bldg["floor_height"]
        total_h_bu = m_to_bu(fh) * floors
        print(
            f"[naranjos] Building '{bldg['name']}': "
            f"{floors} floor(s), {fh} m/floor → {total_h_bu:.2f} BU total"
        )

        obj = _build_building(curve, bldg)
        _move_to_collection(obj, "BSP")
        generated.append(obj)

    # ── borders ───────────────────────────────────────────────────────────
    border_path = border_data.get("path_name", "borders")
    border_curve = _find_curve(svg_objects, border_path, label_map)
    # SVG uses "limites" as the label for the border path
    if border_curve is None:
        border_curve = _find_curve(svg_objects, "limites", label_map)
    if border_curve:
        h = float(border_data["height"])
        print(f"[naranjos] Borders: {h} m → {m_to_bu(h):.2f} BU")
        border_obj = _build_border(border_curve, border_data)
        _move_to_collection(border_obj, "BSP")
        generated.append(border_obj)
    else:
        print(f"[naranjos] WARNING: no curve for borders ('{border_path}').")

    # ── cleanup ───────────────────────────────────────────────────────────
    _cleanup_svg_leftovers(svg_objects)

    print(
        f"[naranjos] Done — {len(generated)} object(s) in BSP collection.\n"
        f"           Wall thickness : {WALL_THICKNESS_BU} BU "
        f"(~{WALL_THICKNESS_BU * M_PER_BU * 100:.0f} cm)\n"
        f"           SVG scale      : {SVG_TO_BU:.4f}"
    )


if __name__ == "__main__":
    import sys

    # Remove default objects (Cube, Light, Camera)
    for obj_name in ("Cube", "Light", "Camera"):
        obj = bpy.data.objects.get(obj_name)
        if obj is not None:
            bpy.data.objects.remove(obj, do_unlink=True)

    generate_naranjos()

    # Save .blend file next to the script (or accept --output via argv)
    blend_out = _DIR / "naranjos.blend"
    for i, arg in enumerate(sys.argv):
        if arg == "--output" and i + 1 < len(sys.argv):
            blend_out = Path(sys.argv[i + 1])
            break
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_out))
    print(f"[naranjos] Saved → {blend_out}")
