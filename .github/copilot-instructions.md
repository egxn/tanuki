# Tanuki — Copilot Workspace Instructions

Tanuki is a **declarative Python DSL for procedural 3D geometry** that compiles to multiple backends (Blender, OpenSCAD, JSCAD, OpenCascade.js).

## Architecture (3 layers)

```
Python DSL  →  Immutable IR graph  →  Backend compiler  →  Output file
```

| Layer | Module | Role |
|-------|--------|------|
| DSL | `tanuki.dsl` | Pure functions that build IR trees |
| IR | `tanuki.ir` | Frozen dataclasses representing geometry |
| Backend | `tanuki.backends` | Compiles IR to target-specific source |

## Project layout

```
src/tanuki/
├── dsl/            # User-facing API (pure functions)
│   ├── context.py       # model(), output()
│   ├── primitives.py    # cube, sphere, cylinder, cone, point, circle, grid, ico_sphere, line
│   ├── operations.py    # union, difference, intersect, join
│   ├── transforms.py    # translate, rotate, scale_by, place, transform, set_position, pipe
│   ├── curves.py        # curve_arc, curve_circle, curve_line, curve_star, bezier_segment, …
│   ├── curve_ops.py     # fill_curve, fillet_curve, resample_curve, trim_curve, …
│   ├── mesh_ops.py      # extrude, subdivide, subdivide_surface, curve_to_mesh, …
│   ├── instancing.py    # clones
│   ├── instance_ops.py  # realize_instances, rotate_instances, scale_instances, …
│   ├── material_ops.py  # set_material, replace_material, set_material_index
│   ├── field_nodes.py   # 33+ field inputs (position, normal, index, radius, …)
│   ├── math_ops.py      # 40+ scalar & vector math ops
│   ├── attribute_ops.py # store_named_attribute, remove_named_attribute
│   ├── volume_ops.py    # volume_cube, points_to_volume, distribute_points_in_volume
│   ├── other_ops.py     # 50+ misc ops (convex_hull, bounding_box, delete_geometry, …)
│   ├── importers.py     # import_obj, import_stl, collection_info, object_info, …
│   ├── export.py        # combined_export, individual_export
│   └── custom/          # Project-specific custom node wrappers
├── ir/             # Immutable IR (frozen dataclasses)
│   ├── nodes.py         # IRNode, IRPrimitive, IRBoolean, IRTransform, IRJoin, …
│   └── graph.py         # IRGraph container
├── backends/
│   ├── __init__.py      # render() entry point
│   └── blender/
│       ├── compiler.py  # IR → standalone bpy Python script
│       ├── runtime.py   # IR → direct bpy execution inside Blender
│       └── node_map.py  # Auto-generated registry of 223 Blender GN nodes
├── codegen/        # Code generation utilities
└── tests/          # pytest test suite (unit + integration)
```

## Key DSL patterns

```python
from tanuki.dsl import *

# 1. Always wrap models in model() context manager
with model("part_name") as ctx:
    # 2. Create primitives
    base = cube(width, depth, height, "label")

    # 3. Chain transforms with | (pipe operator)
    part = base | translate(x, y, z) | rotate(rx, ry, rz)

    # 4. Boolean operations
    result = difference(base, [hole1, hole2])
    result = union([part_a, part_b])

    # 5. Mark output
    output(result)

graph = ctx.graph  # IRGraph, ready for render/export
```

## Export patterns

```python
from tanuki.dsl.export import combined_export, individual_export

# Multiple models → single .py file (one setup_<name>() per model)
combined_export([graph_a, graph_b], "output.py")

# Multiple models → separate files in a directory
individual_export([graph_a, graph_b], "output_dir/")
```

## File naming conventions

- Generated output files (`*_blender.py`, `*.scad`) go to `lens_machine_output/` or named dirs

## Key invariants

- **All DSL functions are pure** — they return IR nodes, never mutate state
- **`|` composes transforms** — `node | op` returns a new wrapped node; original is unchanged
- **`model()` uses `contextvars`** — thread-safe, nesting not required
- **IR nodes are frozen** — never modify a node after creation
- **Labels are optional** — pass a string as the last arg to most constructors for debug clarity

## Running tests

```bash
cd src/tanuki && pip install -e ".[dev]"
pytest src/tanuki/tests/
```

## Instruction files in `.github/instructions/`

| File | Covers |
|------|--------|
| `dsl.instructions.md` | DSL patterns, all modules, pipe composition |
| `backends.instructions.md` | Backend compilation and render() API |
