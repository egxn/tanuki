---
applyTo: "src/tanuki/backends/**,*_gen.py"
---

# Backends — Compilation and render() API

## render() — unified entry point

```python
from tanuki.backends import render

render(graph, target="blender", mode="script", output_path="out.py")
```

| Parameter | Values | Default |
|-----------|--------|---------|
| `target` | `"blender"`, `"openscad"`, `"jscad"`, `"opencascade"` | `"blender"` |
| `mode` | `"script"`, `"direct"` (blender only) | `"script"` |
| `output_path` | file path, directory path, or `None` | `None` (returns string) |

### Return value

| Input | Output |
|-------|--------|
| Single graph, no `output_path` | Source **string** |
| Single graph, `output_path` | `Path` of written file |
| `[graphs]`, `output_path="file.py"` | Single combined `Path` |
| `[graphs]`, `output_path="dir/"` | `list[Path]`, one per graph |
| `mode="direct"` | `None` (executes in-process via bpy) |

## Per-target output formats

| Target | Extension | Description |
|--------|-----------|-------------|
| `blender` | `.py` | Standalone `bpy` Python script; run with `blender --background --python` |
| `openscad` | `.scad` | Native OpenSCAD CSG code |
| `jscad` | `.jscad` | `@jscad/modeling` CommonJS module |
| `opencascade` | `.js` | OpenCascade.js BREP ES module |

## Blender backend

### script mode (default)

Generates a standalone Python file with one `setup_<name>()` function per model. Run it directly in Blender:

```bash
blender --background --python my_model.py
```

The generated script:
1. Creates a mesh object
2. Adds a **Geometry Nodes** modifier
3. Builds the node tree node-by-node and links sockets

### direct mode (inside Blender only)

Executes the IR graph without writing a file. Requires a running Blender session:

```python
render(graph, target="blender", mode="direct")
```

### compiler.py internals

Located at `src/tanuki/backends/blender/compiler.py`.

- `compile_to_source(graph: IRGraph) -> str` — returns the full bpy script as a string
- `compile_to_script(graph, output_path) -> Path` — writes to disk
- Node type mapping lives in `node_map.py` (auto-generated, 223 GN nodes)

## Export helpers (preferred for mori scripts)

For multi-part models, use the high-level export helpers directly instead of `render()`:

```python
from tanuki.dsl.export import combined_export, individual_export

# All parts → single .py (one setup_<name>() per model graph)
path = combined_export([graph_a, graph_b, graph_c], "assembly.py")

# Each part → its own file in a directory
paths = individual_export([graph_a, graph_b], "parts_dir/")
```

These are the same helpers called internally by `render()` for batch blender exports.

## Generator scripts (repo root `*_gen.py`)

Top-level `*_gen.py` files are thin CLI wrappers over their corresponding `mori` module:

```python
# lens_machine_gen.py — typical pattern
from tanuki.mori.print_labo.lens_machine import ALL_PARTS
from tanuki.dsl.export import combined_export

path = combined_export(ALL_PARTS, "lens_machine_output/lens_machine_blender.py")
print(f"Written: {path}")
```

Run them directly from the repo root:

```bash
PYTHONPATH=src python lens_machine_gen.py
```

## Testing backends

```bash
# Unit tests (IR → source correctness)
pytest src/tanuki/tests/test_compiler.py

# Integration tests (full round-trip)
pytest src/tanuki/tests/test_integration.py
```
