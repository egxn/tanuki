# Tanuki

**A declarative Python DSL for procedural geometry that compiles to Blender Geometry Nodes.**

Write models as pure Python functions — Tanuki compiles them into standalone Blender scripts.

---

## Quickstart

```python
from tanuki.dsl import *
from tanuki.backends import render

def create_belt_holder():
    with model("belt_holder") as ctx:
        base = cylinder(5.5, 15, "base")
        hole = cylinder(4.5, 15, "hole")
        result = difference(base, [hole])
        output(result)
    return ctx.graph

graph = create_belt_holder()
render(graph, target="blender", mode="script", output_path="belt_holder.py")
```

Running `blender --background --python belt_holder.py` creates the geometry in Blender.

---

## Install

```bash
cd src/tanuki
pip install -e ".[dev]"
```

---

## Architecture

```
Python DSL → Immutable IR (frozen dataclasses) → Backend compiler → Blender script / direct bpy
```

Three layers, functional paradigm throughout:

1. **DSL** — Pure functions (`cube`, `union`, `transform`, etc.) build an IR tree
2. **IR** — Immutable geometry graph (`IRPrimitive`, `IRBoolean`, `IRTransform`, …)
3. **Backend** — Compiles IR to executable Python/bpy scripts or runs directly in Blender

---

## API Reference

### Primitives

```python
cube(x, y, z, label="", position=None, rotation=None, scale=None, translation=None)
sphere(r, label="", segments=None, rings=None, ...)
cylinder(r, depth, label="", vertices=32, ...)
cone(r_top, r_bottom, depth, label="", ...)
point(x=0, y=0, z=0, label="")
```

### Boolean operations

```python
union([a, b, c])              # merge geometries
difference(base, [hole1, hole2])  # subtract from base
intersect([a, b])             # keep only intersection
join([a, b])                  # join without boolean
```

### Transforms

```python
transform(node, translation=(x, y, z), rotation=(rx, ry, rz), scale=(sx, sy, sz))
set_position(node, position=(x, y, z))
```

Rotation is in **degrees** — the compiler converts to radians automatically.

### Instancing

```python
positions = [(0, 0, 0), (10, 0, 0), (20, 0, 0)]
clones(node, positions)    # instance node at each point
```

### Context

```python
with model("name") as ctx:
    # ... build geometry ...
    output(result_node)

graph = ctx.graph  # IRGraph ready for compilation
```

---

## Rendering

```python
from tanuki.backends import render

# Generate a standalone .py script (Blender Geometry Nodes)
render(graph, target="blender", mode="script", output_path="output.py")

# Execute directly inside Blender (requires bpy)
render(graph, target="blender", mode="direct")

# Other targets
render(graph, target="opencascade", output_path="output.js")   # opencascade.js ES module
render(graph, target="openscad", output_path="output.scad")    # OpenSCAD
render(graph, target="jscad", output_path="output.jscad")      # JSCAD CommonJS module
```

See `src/tanuki/backends/README.md` for what each backend supports.

---

## Example: Claw with sprocket instancing

```python
from tanuki.dsl import *

def create_claw():
    with model("claw") as ctx:
        leg_l = cube(5.5, 50, 2, "leg_l", position=(14.75, 0, 0))
        leg_r = cube(5.5, 50, 2, "leg_r", position=(-14.75, 0, 0))
        top = cube(35, 10, 2, "top", position=(0, 25, 0))

        hook = cylinder(12, 2, "hook", position=(0, 35, 0))
        h_hook = cylinder(8, 2, "h_hook", position=(0, 35, 0))
        hook = difference(hook, [h_hook])

        sprocket = cube(2.5, 1.8, 3, "sprocket", position=(0, 0, 1))
        positions = [(x, y, 0) for y in range(9) for x in [14, -14]]
        sprockets = clones(sprocket, positions)

        claw = union([leg_l, leg_r, top, hook, sprockets])
        output(claw)
    return ctx.graph
```

---

## Auto-generated node metadata

The `codegen/generate_nodes.py` script reads Blender's 223 geometry node definitions from `docs/geometry_nodes_categories/*.json` and generates `backends/blender/node_map.py` with:

- `NODE_REGISTRY` — full metadata for each node
- `DSL_PRIMITIVE_MAP` — DSL primitive → bpy node type
- `NODE_INPUTS` / `NODE_OUTPUTS` — socket info per node

Regenerate with:

```bash
PYTHONPATH=src python -m tanuki.codegen.generate_nodes
```

---

## Tests

```bash
# Unit tests (no Blender required)
PYTHONPATH=src pytest src/tanuki/tests/ -v
```

---

## Project structure

```
src/tanuki/
├── ir/                   # Immutable intermediate representation
│   ├── nodes.py          # Frozen dataclass IR node types
│   └── graph.py          # IRGraph container + pure operations
├── dsl/                  # Declarative user API
│   ├── primitives.py     # cube, sphere, cylinder, cone, point, circle, grid, ...
│   ├── operations.py     # union, difference, intersect, join
│   ├── transforms.py     # transform, set_position, translate, rotate, scale_by
│   ├── instancing.py     # clones
│   ├── instance_ops.py   # realize_instances, split_to_instances, ...
│   ├── mesh_ops.py        # extrude, subdivide, bevel, dual_mesh, ...
│   ├── curves.py          # curve_arc, curve_circle, bezier_segment, ...
│   ├── curve_ops.py       # fillet_curve, resample_curve, trim_curve, ...
│   ├── field_nodes.py     # position, normal, index, edge_angle, ...
│   ├── material_ops.py    # set_material, replace_material
│   ├── volume_ops.py      # volume_cube, points_to_volume
│   ├── attribute_ops.py   # store_named_attribute, remove_named_attribute
│   ├── importers.py       # import_obj/stl/ply/csv/vdb/svg, collection_info
│   ├── other_ops.py       # convex_hull, bounding_box, raycast, switch, ...
│   ├── export.py          # graph export helpers
│   ├── context.py         # model() context manager, output()
│   └── custom/            # non-generated helper ops (e.g. mesh_analysis)
├── codegen/              # Auto-generation from node metadata
│   └── generate_nodes.py
├── backends/
│   ├── README.md         # per-backend support matrix
│   ├── blender/
│   │   ├── compiler.py   # IR → standalone .py script (Geometry Nodes)
│   │   ├── runtime.py    # IR → direct bpy execution
│   │   └── node_map.py   # Auto-generated node registry (223 nodes)
│   ├── opencascade/
│   │   └── compiler.py   # IR → .js ES module for opencascade.js (BREP)
│   ├── openscad/
│   │   └── compiler.py   # IR → .scad
│   └── jscad/
│       └── compiler.py   # IR → .jscad CommonJS module
└── tests/
    ├── test_ir.py
    ├── test_dsl.py
    ├── test_compiler.py
    ├── test_mesh_analysis_custom.py
    └── test_new_nodes.py
```

---

## Design principles

- **Functional first** — Pure functions, frozen dataclasses, immutable IR trees. Mutable state isolated to context manager and bpy runtime.
- **Composition** — `output(difference(cube(...), [cylinder(...)]))` — geometry is composed through function calls.
- **Lazy evaluation** — The DSL builds an IR graph, nothing executes until `render()` is called.
- **Backend agnostic** — The IR is independent of Blender; the same IR already compiles to OpenCascade.js, OpenSCAD, and JSCAD, not just Blender.

---

## Status

Implemented:
- Python DSL with primitives, booleans, transforms, instancing, curves, fields, and more
- Immutable IR with frozen dataclasses
- Four backends: Blender Geometry Nodes (script + direct bpy), OpenCascade.js, OpenSCAD, JSCAD
- Auto-generated Blender node registry (223 geometry nodes, ~90% coverage)

See `src/tanuki/backends/README.md` for the full per-backend support matrix.

---

# License

MIT

---

# Contributing

Contributions, ideas, and experiments are welcome.
