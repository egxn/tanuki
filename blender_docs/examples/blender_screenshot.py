"""Blender screenshot utility — run an example and capture a viewport render.

Usage (from the repo root):

    blender --background --python blender_docs/examples/blender_screenshot.py -- \\
        --script blender_docs/examples/primitives_showcase.py \\
        --output blender_docs/images/primitives_showcase.png \\
        --width  1280 \\
        --height  720

The utility:
  1. Executes the Tanuki-generated bpy script to build the geometry nodes.
  2. Configures a camera that frames all objects.
  3. Renders a screenshot to the specified path.
"""

from __future__ import annotations

import argparse
import math
import os
import sys
from pathlib import Path

# --- Blender imports (only available inside Blender) -----------------------
import bpy  # type: ignore
import mathutils  # type: ignore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_args() -> argparse.Namespace:
    """Parse CLI args after Blender's ``--`` separator."""
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []

    parser = argparse.ArgumentParser(description="Blender screenshot utility")
    parser.add_argument("--script", required=True, help="Path to the generated .py script")
    parser.add_argument("--output", required=True, help="Output image path (.png)")
    parser.add_argument("--width", type=int, default=1280, help="Image width")
    parser.add_argument("--height", type=int, default=720, help="Image height")
    return parser.parse_args(argv)


def _clean_scene() -> None:
    """Remove all objects, meshes, and materials from the default scene."""
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)


def _run_tanuki_script(script_path: str) -> None:
    """Generate and exec the Tanuki bpy script."""
    real_path = os.path.realpath(script_path)

    # If the script is a Tanuki DSL source (imports tanuki), run it under
    # the host Python so the compiler produces the bpy script beside it.
    # Otherwise assume it is already a bpy script and exec directly.

    src = Path(real_path).read_text()
    if "from tanuki" in src or "import tanuki" in src:
        # Run the DSL script in a subprocess so tanuki can resolve properly.
        import subprocess

        env = os.environ.copy()
        proj_root = str(Path(__file__).resolve().parents[2])
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            os.path.join(proj_root, "src") + (os.pathsep + existing if existing else "")
        )
        subprocess.check_call(
            [sys.executable, real_path],
            env=env,
        )

        # The DSL script writes a *_gen.py beside itself.
        gen_path = Path(real_path).with_name(
            Path(real_path).stem + "_gen.py"
        )
        if not gen_path.exists():
            # Fallback: look in cwd
            gen_path = Path(Path(real_path).stem + "_gen.py")
        src = gen_path.read_text()

    exec(compile(src, str(real_path), "exec"), {"__name__": "__main__"})


def _bounds_center_size():
    """Return (center, size) bounding box of all mesh objects."""
    min_co = mathutils.Vector((float("inf"),) * 3)
    max_co = mathutils.Vector((float("-inf"),) * 3)

    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        # Force dependency graph evaluation
        dg = bpy.context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(dg)
        bbox = [obj_eval.matrix_world @ mathutils.Vector(c) for c in obj_eval.bound_box]
        for v in bbox:
            min_co.x = min(min_co.x, v.x)
            min_co.y = min(min_co.y, v.y)
            min_co.z = min(min_co.z, v.z)
            max_co.x = max(max_co.x, v.x)
            max_co.y = max(max_co.y, v.y)
            max_co.z = max(max_co.z, v.z)

    center = (min_co + max_co) / 2
    size = max_co - min_co
    return center, size


def _setup_camera(width: int, height: int) -> None:
    """Create a camera that frames all objects from a 3/4 perspective."""
    center, size = _bounds_center_size()
    diagonal = size.length or 2.0

    # Position camera at 3/4 view angle
    angle_h = math.radians(40)
    angle_v = math.radians(25)
    distance = diagonal * 2.0

    cam_loc = center + mathutils.Vector((
        distance * math.cos(angle_v) * math.sin(angle_h),
        -distance * math.cos(angle_v) * math.cos(angle_h),
        distance * math.sin(angle_v),
    ))

    cam_data = bpy.data.cameras.new("ScreenshotCam")
    cam_data.lens = 50
    cam_obj = bpy.data.objects.new("ScreenshotCam", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)

    cam_obj.location = cam_loc
    direction = center - cam_loc
    rot_quat = direction.to_track_quat("-Z", "Y")
    cam_obj.rotation_euler = rot_quat.to_euler()

    bpy.context.scene.camera = cam_obj

    # Resolution
    bpy.context.scene.render.resolution_x = width
    bpy.context.scene.render.resolution_y = height
    bpy.context.scene.render.resolution_percentage = 100


def _setup_lighting() -> None:
    """Set up a light World background for Workbench rendering."""
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.color = (0.85, 0.85, 0.88)


def _setup_viewport_shading() -> None:
    """Configure all 3D viewports: Solid + X-Ray + Random color + Outline."""
    for area in bpy.context.screen.areas:
        if area.type != "VIEW_3D":
            continue
        for space in area.spaces:
            if space.type != "VIEW_3D":
                continue
            space.shading.type = "SOLID"
            space.shading.color_type = "RANDOM"
            space.shading.show_xray = True
            space.shading.xray_alpha = 0.5
            space.shading.show_object_outline = True


def _render_screenshot(output_path: str) -> None:
    """Render the scene via Workbench engine and save to *output_path*."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    scene = bpy.context.scene
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(out.resolve())

    # Workbench engine — Solid shading with X-Ray + Random color
    scene.render.engine = "BLENDER_WORKBENCH"

    s = scene.display.shading
    s.type = "SOLID"
    s.light = "STUDIO"
    s.color_type = "RANDOM"
    s.show_xray = True
    s.xray_alpha = 0.5
    s.show_object_outline = True
    s.object_outline_color = (0.0, 0.0, 0.0)

    # Light background via World color
    s.background_type = "WORLD"

    # Anti-aliasing
    scene.display.render_aa = "8"

    bpy.ops.render.render(write_still=True)
    print(f"Screenshot saved to: {out.resolve()}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    args = _parse_args()

    _clean_scene()
    _run_tanuki_script(args.script)
    _setup_lighting()
    _setup_camera(args.width, args.height)
    _setup_viewport_shading()
    _render_screenshot(args.output)


if __name__ == "__main__":
    main()
