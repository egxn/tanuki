"""Naranjos map — DSL-based parametric building, hall, roof, and border generator.

Uses the Tanuki Geometry Nodes DSL to create **parametric** node trees
for each building, hall, roof, and border. The resulting GN modifiers stay
live (not baked) so that floor count, height, wall thickness, etc. can be
adjusted directly in Blender.

Run inside Blender::

    import importlib, tanuki.mori.halo_maps.naranjos.generate_dsl as gd
    importlib.reload(gd); gd.generate_naranjos_dsl()

Or from CLI::

    blender --background --python src/tanuki/mori/halo_maps/naranjos/generate_dsl.py
"""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

# Ensure tanuki is importable when running standalone inside Blender
_SRC_ROOT = str(Path(__file__).resolve().parents[4])
if _SRC_ROOT not in sys.path:
    sys.path.insert(0, _SRC_ROOT)

import bpy
import bmesh

# Tanuki DSL imports
from tanuki.dsl import (
    model,
    output,
    object_info,
    curve_to_mesh,
    translate,
    join,
    clones,
    realize_instances,
    set_spline_cyclic,
)
from tanuki.dsl.curves import curve_line, curve_quadrilateral
from tanuki.backends.blender.compiler import compile_to_source

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DIR = Path(__file__).resolve().parent

M_PER_BU = 0.55
WALL_THICKNESS_BU = 0.22
SLAB_THICKNESS_BU = 0.05
DEFAULT_INTER_FLOOR_HEIGHT_M = 2.28

# SVG → BU scale (calibrated for this map's raw import).
SVG_TO_BU = 0.005

CURVE_RESOLUTION = 12


def m_to_bu(metres: float) -> float:
    return metres / M_PER_BU


def bu_to_m(blam_units: float) -> float:
    return blam_units * M_PER_BU


# ---------------------------------------------------------------------------
# SVG label → id mapping
# ---------------------------------------------------------------------------

_INK_NS = "http://www.inkscape.org/namespaces/inkscape"


def _parse_svg_label_map(svg_path: str | Path) -> dict[str, str]:
    tree = ET.parse(svg_path)
    label_to_id: dict[str, str] = {}
    for elem in tree.iter():
        label = elem.get(f"{{{_INK_NS}}}label")
        svg_id = elem.get("id")
        if label and svg_id:
            label_to_id[label.lower()] = svg_id
    return label_to_id


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_buildings() -> list[dict]:
    with open(_DIR / "buildings.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    for b in data:
        if "floors" in b and "floor" not in b:
            b["floor"] = b["floors"]
        b.setdefault("floor", 1)
    return data


def _load_borders() -> dict:
    with open(_DIR / "borders.json", "r", encoding="utf-8") as f:
        return json.load(f)


def _load_roofs_halls() -> list[dict]:
    with open(_DIR / "roofs_halls.json", "r", encoding="utf-8") as f:
        return json.load(f)


def _building_floor_count(building: dict) -> int:
    return int(building.get("floor", building.get("floors", 1)))


def _infer_brick_height_m(buildings_data: list[dict]) -> float | None:
    samples: list[float] = []
    for building in buildings_data:
        floor_height = building.get("floor_height")
        bricks_h = building.get("meta", {}).get("bricks_h")
        if floor_height and bricks_h:
            samples.append(float(floor_height) / float(bricks_h))
    if not samples:
        return None
    samples.sort()
    return samples[len(samples) // 2]


def _building_pitch_m(building: dict, brick_height_m: float | None) -> float | None:
    if "floor_height" in building:
        return float(building["floor_height"])
    bricks_h = building.get("meta", {}).get("bricks_h")
    if brick_height_m is not None and bricks_h:
        return float(bricks_h) * brick_height_m
    return None


def _required_building_floors(entry: dict) -> int:
    floor_base = max(int(entry.get("floor_base", 1)), 1)
    if entry.get("kind") == "hall":
        return floor_base
    return max(floor_base - 1, 1)


def _evaluated_object_height_bu(obj: bpy.types.Object) -> float | None:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    eval_mesh = eval_obj.to_mesh()
    try:
        zs = [vert.co.z for vert in eval_mesh.vertices]
        if not zs:
            return None
        return max(zs) - min(zs)
    finally:
        eval_obj.to_mesh_clear()


def _generated_storey_pitch_bu(
    entry: dict,
    buildings_data: list[dict],
    building_objects: dict[str, bpy.types.Object] | None,
) -> float | None:
    if not building_objects:
        return None

    required_floors = _required_building_floors(entry)
    candidates: list[float] = []
    for building in buildings_data:
        floors = _building_floor_count(building)
        if floors < required_floors:
            continue
        obj = building_objects.get(building["name"])
        if obj is None:
            continue
        height_bu = _evaluated_object_height_bu(obj)
        if height_bu is not None:
            candidates.append(round(height_bu / floors, 4))

    if not candidates:
        return None

    return Counter(candidates).most_common(1)[0][0]


def _storey_pitch_m(entry: dict, buildings_data: list[dict]) -> float:
    if "pitch_m" in entry:
        return float(entry["pitch_m"])

    brick_height_m = _infer_brick_height_m(buildings_data)
    required_floors = _required_building_floors(entry)
    candidates: list[float] = []
    for building in buildings_data:
        if _building_floor_count(building) < required_floors:
            continue
        pitch_m = _building_pitch_m(building, brick_height_m)
        if pitch_m is not None:
            candidates.append(round(pitch_m, 4))

    if not candidates:
        return DEFAULT_INTER_FLOOR_HEIGHT_M

    return Counter(candidates).most_common(1)[0][0]


def _inter_floor_height_m(entry: dict, buildings_data: list[dict]) -> float:
    return bu_to_m(_entry_height_bu(entry, buildings_data))


def _entry_height_bu(
    entry: dict,
    buildings_data: list[dict],
    building_objects: dict[str, bpy.types.Object] | None = None,
) -> float:
    if "height_bu" in entry:
        return float(entry["height_bu"])
    if "height" in entry:
        return m_to_bu(float(entry["height"]))
    pitch_bu = _generated_storey_pitch_bu(entry, buildings_data, building_objects)
    if pitch_bu is None:
        pitch_bu = m_to_bu(_storey_pitch_m(entry, buildings_data))
    return max(pitch_bu - (2 * SLAB_THICKNESS_BU), 0.0)


def _base_z_offset_bu(entry: dict, level_height_bu: float) -> float:
    """Return the Z start for an inter-floor volume.

    ``floor_base`` indexes the upper floor bound of the span:
      - floor_base=2 → volume spans between floors 1 and 2
      - floor_base=3 → volume spans between floors 2 and 3
    """
    floor_base = max(int(entry.get("floor_base", 1)) - 1, 0)
    return floor_base * level_height_bu


def _entry_z_start_bu(
    entry: dict,
    level_height_bu: float,
    buildings_data: list[dict],
    building_objects: dict[str, bpy.types.Object] | None = None,
) -> float:
    if "z_start_bu" in entry:
        return float(entry["z_start_bu"])
    pitch_bu = _generated_storey_pitch_bu(entry, buildings_data, building_objects)
    if pitch_bu is None:
        pitch_bu = m_to_bu(_storey_pitch_m(entry, buildings_data))
    return _base_z_offset_bu(entry, pitch_bu) + SLAB_THICKNESS_BU


# ---------------------------------------------------------------------------
# SVG import
# ---------------------------------------------------------------------------

def _import_svg() -> tuple[list[bpy.types.Object], dict[str, str]]:
    svg_path = _DIR / "map.svg"
    label_map = _parse_svg_label_map(svg_path)

    before = set(bpy.data.objects)
    bpy.ops.import_curve.svg(filepath=str(svg_path))
    after = set(bpy.data.objects)
    new_objs = list(after - before)

    if not new_objs:
        return new_objs, label_map

    for obj in new_objs:
        obj.scale = (SVG_TO_BU, SVG_TO_BU, SVG_TO_BU)
        if obj.type == "CURVE":
            obj.data.resolution_u = CURVE_RESOLUTION

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
    lower = path_name.lower()
    svg_id = label_map.get(lower)
    if svg_id:
        for obj in objects:
            if obj.type == "CURVE" and obj.name.startswith(svg_id):
                return obj
    for obj in objects:
        if obj.type == "CURVE" and lower in obj.name.lower():
            return obj
    for obj in objects:
        if obj.type == "CURVE" and lower in obj.data.name.lower():
            return obj
    print(f"[naranjos-dsl] No match for '{path_name}' (svg_id={svg_id}).")
    return None


# ---------------------------------------------------------------------------
# DSL graph builders
# ---------------------------------------------------------------------------

def _building_graph(
    name: str,
    curve_obj_name: str,
    num_floors: int,
    floor_height_bu: float,
    wall_thickness_bu: float,
    slab_thickness_bu: float,
    z_start_bu: float = 0.0,
):
    """Build an IRGraph for one or more sealed storey volumes.

    Strategy (all in Geometry Nodes):
        1. Object Info → footprint curve
        2. Set Spline Cyclic (ensure closed)
        3. Wall profile = Curve Quadrilateral (wall_thickness × floor_height)
        4. Curve to Mesh (footprint, profile) → hollow walls for one floor
        5. Sweep the footprint along a short vertical line → closed floor slab
        6. Ceiling slab = same sweep translated up
        7. Join walls + floor + ceiling → one floor module
        8. Instance on Points at (0,0, i*floor_height) for each floor
        9. Realize instances → final geometry
    """
    with model(f"gn_{name}") as ctx:
        # Footprint curve from the imported SVG object
        footprint = object_info(curve_obj_name)
        footprint = footprint | set_spline_cyclic(cyclic=True)

        # Wall cross-section: rectangle (wall_thickness × floor_height)
        wall_profile = curve_quadrilateral(wall_thickness_bu, floor_height_bu)

        # Walls for one floor: sweep profile along footprint.
        # curve_to_mesh centres the profile on the path, so the wall
        # extends from -floor_height/2 to +floor_height/2.  Shift up
        # so walls sit on [0, floor_height] matching the slabs.
        walls = (
            footprint
            | curve_to_mesh(profile=wall_profile, fill_caps=True)
            | translate(0, 0, floor_height_bu / 2)
        )

        slab_path = curve_line(
            start=(0.0, 0.0, 0.0),
            end=(0.0, 0.0, slab_thickness_bu),
        )
        floor_slab = slab_path | curve_to_mesh(profile=footprint, fill_caps=True)
        ceiling_slab = (
            slab_path
            | curve_to_mesh(profile=footprint, fill_caps=True)
            | translate(0, 0, floor_height_bu - slab_thickness_bu)
        )

        # One complete floor module
        one_floor = join([walls, floor_slab, ceiling_slab])

        # Stack floors using Instance on Points
        floor_positions = [
            (0.0, 0.0, i * floor_height_bu) for i in range(num_floors)
        ]
        stacked = clones(one_floor, floor_positions)
        result = stacked | realize_instances()
        if z_start_bu:
            result = result | translate(0, 0, z_start_bu)

        output(result)

    return ctx.graph


def _roof_or_hall_graph(
    name: str,
    curve_obj_name: str,
    level_height_bu: float,
    wall_thickness_bu: float,
    slab_thickness_bu: float,
    z_start_bu: float,
):
    return _building_graph(
        name,
        curve_obj_name,
        num_floors=1,
        floor_height_bu=level_height_bu,
        wall_thickness_bu=wall_thickness_bu,
        slab_thickness_bu=slab_thickness_bu,
        z_start_bu=z_start_bu,
    )


def _border_graph(
    curve_obj_name: str,
    height_bu: float,
    wall_thickness_bu: float,
):
    """Build an IRGraph for border walls.

    Strategy:
        1. Object Info → border curve
        2. Wall profile = Curve Quadrilateral (wall_thickness × height)
        3. Curve to Mesh (border path, profile) → border wall with thickness
    """
    with model("gn_borders") as ctx:
        border_curve = object_info(curve_obj_name)
        wall_profile = curve_quadrilateral(wall_thickness_bu, height_bu)
        walls = (
            border_curve
            | curve_to_mesh(profile=wall_profile, fill_caps=True)
            | translate(0, 0, height_bu / 2)
        )
        output(walls)

    return ctx.graph


# ---------------------------------------------------------------------------
# GN tree application helpers
# ---------------------------------------------------------------------------

def _exec_gn_setup(object_name: str, gn_source: str) -> bpy.types.Object:
    """Execute compiled DSL source which creates the object + GN modifier.

    The compiled ``setup(object_name)`` function:
      - Creates a mesh object named *object_name*
      - Adds a GeometryNodes modifier
      - Builds the full node tree

    The modifier is kept **live** so the GN tree stays parametric.
    Returns the created Blender object.
    """
    namespace: dict = {"bpy": bpy}
    exec(compile(gn_source, f"<gn_{object_name}>", "exec"), namespace)
    # Call the setup function with the desired object name
    namespace["setup"](object_name=object_name)
    return bpy.data.objects[object_name]


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


def _cleanup_svg_collection() -> None:
    svg_stem = Path(_DIR / "map.svg").stem.lower()
    for coll in list(bpy.data.collections):
        if svg_stem in coll.name.lower() and len(coll.objects) == 0:
            bpy.data.collections.remove(coll)


# ---------------------------------------------------------------------------
# Validators (on evaluated mesh)
# ---------------------------------------------------------------------------

def _validate_object(obj_name: str) -> dict[str, list[str]]:
    """Run BSP validators on the *evaluated* (GN-applied) mesh."""
    obj = bpy.data.objects.get(obj_name)
    if obj is None or obj.type != "MESH":
        return {"error": [f"Object '{obj_name}' not found or not a mesh."]}

    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    eval_mesh = eval_obj.to_mesh()

    bm = bmesh.new()
    bm.from_mesh(eval_mesh)
    bm.faces.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    results: dict[str, list[str]] = {}

    # closed geometry
    boundary = [e for e in bm.edges if len(e.link_faces) < 2]
    results["closed_geometry"] = (
        [f"{len(boundary)} boundary edge(s)"]
        if boundary else []
    )

    # manifold edges
    non_manifold = [e for e in bm.edges if len(e.link_faces) != 2]
    results["manifold_edges"] = (
        [f"{len(non_manifold)} non-manifold edge(s)"]
        if non_manifold else []
    )

    # polygon budget
    face_count = len(bm.faces)
    results["polygon_budget"] = (
        [f"{face_count:,} faces (consider simplifying)"]
        if face_count > 10_000 else []
    )

    # normals
    degenerate = [f for f in bm.faces if f.normal.length < 1e-6]
    results["normals"] = (
        [f"{len(degenerate)} degenerate face(s)"]
        if degenerate else []
    )

    bm.free()
    eval_obj.to_mesh_clear()

    return results


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_naranjos_dsl() -> None:
    """Generate Naranjos map volumes with parametric Geometry Nodes.

    Each building, hall, roof, and border gets a **live GN modifier** compiled from the
    Tanuki DSL.  Parameters (floor height, wall thickness, etc.) are baked
    into the node tree but can be adjusted by editing node values in Blender.
    """
    buildings_data = _load_buildings()
    roofs_halls_data = _load_roofs_halls()
    border_data = _load_borders()

    print("[naranjos-dsl] Importing map.svg …")
    svg_objects, label_map = _import_svg()

    if not svg_objects:
        print("[naranjos-dsl] ERROR: No objects imported from SVG.")
        return

    print(f"[naranjos-dsl] Imported {len(svg_objects)} SVG objects.")

    generated: list[bpy.types.Object] = []
    building_objects: dict[str, bpy.types.Object] = {}

    # ── buildings ─────────────────────────────────────────────────────────
    for bldg in buildings_data:
        path_name = bldg["path_name"]
        curve = _find_curve(svg_objects, path_name, label_map)
        if curve is None:
            print(f"[naranjos-dsl] WARNING: no curve for '{path_name}' — skipped.")
            continue

        name = bldg["name"]
        num_floors = bldg.get("floor", 1)
        floor_height_bu = m_to_bu(bldg["floor_height"])
        total_h_bu = floor_height_bu * num_floors

        print(
            f"[naranjos-dsl] Building '{name}': "
            f"{num_floors} floor(s), {bldg['floor_height']} m/floor "
            f"→ {total_h_bu:.2f} BU total"
        )

        # Build DSL graph → compile → GN source
        graph = _building_graph(
            name, curve.name, num_floors,
            floor_height_bu, WALL_THICKNESS_BU, SLAB_THICKNESS_BU,
        )
        gn_src = compile_to_source(graph)

        # Execute compiled GN setup (creates object + live modifier)
        obj = _exec_gn_setup(name, gn_src)
        _move_to_collection(obj, "BSP")

        # Keep the footprint curve visible for reference
        _move_to_collection(curve, "DEBUG")

        generated.append(obj)
        building_objects[name] = obj

    # ── halls & roofs ─────────────────────────────────────────────────────
    for entry in roofs_halls_data:
        path_name = entry["path_name"]
        curve = _find_curve(svg_objects, path_name, label_map)
        if curve is None:
            print(f"[naranjos-dsl] WARNING: no curve for '{path_name}' — skipped.")
            continue

        name = entry["name"]
        kind = entry.get("kind", "volume")
        level_height_bu = _entry_height_bu(entry, buildings_data, building_objects)
        level_height_m = bu_to_m(level_height_bu)
        pitch_bu = _generated_storey_pitch_bu(entry, buildings_data, building_objects)
        if pitch_bu is None:
            pitch_bu = m_to_bu(_storey_pitch_m(entry, buildings_data))
        z_start_bu = _entry_z_start_bu(
            entry,
            level_height_bu,
            buildings_data,
            building_objects,
        )
        placement = (
            f"z={z_start_bu:.2f} BU (override)"
            if "z_start_bu" in entry
            else (
                f"between floors {max(int(entry.get('floor_base', 1)) - 1, 0)} "
                f"and {entry.get('floor_base', 1)}, z={z_start_bu:.2f} BU "
                f"within pitch {pitch_bu:.2f} BU"
            )
        )

        print(
            f"[naranjos-dsl] {kind.title()} '{name}': "
            f"{placement}, height {level_height_bu:.2f} BU "
            f"({level_height_m:.2f} m)"
        )

        graph = _roof_or_hall_graph(
            name,
            curve.name,
            level_height_bu,
            WALL_THICKNESS_BU,
            SLAB_THICKNESS_BU,
            z_start_bu,
        )
        gn_src = compile_to_source(graph)

        obj = _exec_gn_setup(name, gn_src)
        _move_to_collection(obj, "BSP")
        _move_to_collection(curve, "DEBUG")
        generated.append(obj)

    # ── borders ───────────────────────────────────────────────────────────
    border_path = border_data.get("path_name", "borders")
    border_curve = _find_curve(svg_objects, border_path, label_map)
    if border_curve is None:
        border_curve = _find_curve(svg_objects, "limites", label_map)

    if border_curve:
        h_bu = m_to_bu(float(border_data["height"]))
        print(f"[naranjos-dsl] Borders: {border_data['height']} m → {h_bu:.2f} BU")

        graph = _border_graph(border_curve.name, h_bu, WALL_THICKNESS_BU)
        gn_src = compile_to_source(graph)

        obj = _exec_gn_setup("borders", gn_src)
        _move_to_collection(obj, "BSP")
        _move_to_collection(border_curve, "DEBUG")
        generated.append(obj)
    else:
        print("[naranjos-dsl] WARNING: no curve for borders.")

    # ── cleanup unused SVG objects (keep curves used by GN) ───────────────
    used_curves = {
        o.name
        for o in generated
        for m in o.modifiers
        if m.type == "NODES" and m.node_group
    }
    for obj in list(svg_objects):
        # Remove objects not used as curve references
        if obj.name in bpy.data.objects and obj not in generated:
            is_debug = any(
                obj.name in c.objects
                for c in bpy.data.collections
                if c.name == "DEBUG"
            )
            if not is_debug:
                bpy.data.objects.remove(obj, do_unlink=True)
    _cleanup_svg_collection()

    # ── validate ──────────────────────────────────────────────────────────
    print("\n[naranjos-dsl] ── Validation ──")
    # Force depsgraph evaluation
    bpy.context.view_layer.update()

    all_ok = True
    for obj in generated:
        results = _validate_object(obj.name)
        failed = {k: v for k, v in results.items() if v}
        passed = [k for k, v in results.items() if not v]
        if failed:
            all_ok = False
            print(f"  {obj.name}:")
            for k, msgs in failed.items():
                for msg in msgs:
                    print(f"    [WARN] {k}: {msg}")
            for k in passed:
                print(f"    [OK]   {k}")
        else:
            print(f"  {obj.name}: all checks passed ✓")

    status = "ALL PASSED" if all_ok else "WARNINGS — see above"
    print(
        f"\n[naranjos-dsl] Done — {len(generated)} object(s) in BSP.\n"
        f"           Wall thickness : {WALL_THICKNESS_BU} BU "
        f"(~{WALL_THICKNESS_BU * M_PER_BU * 100:.0f} cm)\n"
        f"           Slab thickness : {SLAB_THICKNESS_BU} BU\n"
        f"           SVG scale      : {SVG_TO_BU}\n"
        f"           Validators     : {status}\n"
        f"           GN modifiers are LIVE — adjust values in Blender."
    )


if __name__ == "__main__":
    import sys

    for obj_name in ("Cube", "Light", "Camera"):
        obj = bpy.data.objects.get(obj_name)
        if obj is not None:
            bpy.data.objects.remove(obj, do_unlink=True)

    generate_naranjos_dsl()

    blend_out = _DIR / "naranjos_dsl.blend"
    for i, arg in enumerate(sys.argv):
        if arg == "--output" and i + 1 < len(sys.argv):
            blend_out = Path(sys.argv[i + 1])
            break
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_out))
    print(f"[naranjos-dsl] Saved → {blend_out}")
