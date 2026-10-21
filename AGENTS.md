# AGENTS.md

Guidance for AI coding agents working in this repository.

## What this project is

Tanuki is a declarative Python DSL for procedural geometry. User code builds an
immutable IR graph (frozen dataclasses), which backend compilers turn into
output for Blender Geometry Nodes, OpenCascade.js, OpenSCAD, or JSCAD.

Pipeline: `Python DSL → Immutable IR → Backend compiler → generated script / direct execution`

## Layout

```
src/tanuki/
├── ir/                   # Frozen dataclass IR nodes + IRGraph container
├── dsl/                  # Declarative user-facing API (primitives, ops, transforms, curves, fields, ...)
│   └── custom/           # Non-generated helper ops (e.g. mesh_analysis)
├── codegen/              # generate_nodes.py — regenerates backends/blender/node_map.py from Blender's node JSON
├── backends/
│   ├── blender/          # compiler.py (IR → .py bpy script), runtime.py (direct bpy execution), node_map.py (generated)
│   ├── opencascade/      # compiler.py (IR → .js ES module for opencascade.js)
│   ├── openscad/         # compiler.py (IR → .scad)
│   └── jscad/            # compiler.py (IR → .jscad CommonJS module)
└── tests/                # pytest suite (unit tests; integration tests need Blender)
```

There is no `models/` directory in the current tree — don't assume example model
files exist unless you've checked.

See `src/tanuki/backends/README.md` for the full per-backend support matrix
(which primitives/ops each backend supports, approximates, or lacks).

## Install & test

```bash
cd src/tanuki && pip install -e ".[dev]"

# Unit tests (no Blender required)
PYTHONPATH=src pytest src/tanuki/tests/ -v

# Regenerate Blender node registry after changing docs/geometry_nodes_categories/*.json
PYTHONPATH=src python -m tanuki.codegen.generate_nodes
```

## Conventions

- **Functional/immutable throughout.** IR nodes are frozen dataclasses; the DSL
  builds a graph lazily, nothing executes until `render()` is called. Don't
  introduce mutable IR state.
- **Backend-agnostic IR.** New DSL ops should be expressible as plain IR nodes
  that each backend compiler can choose to support, approximate, or ignore —
  don't leak Blender-specific concepts into `ir/`.
- When adding a new DSL op or primitive, check whether `backends/blender/node_map.py`
  needs a corresponding entry — it's generated, so prefer updating
  `codegen/generate_nodes.py` / the source JSON over hand-editing it, unless
  the change is backend-specific glue in `compiler.py`.
- Keep `backends/README.md`'s support matrix in sync when adding/removing
  per-backend op support.
