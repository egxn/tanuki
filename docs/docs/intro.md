---
id: intro
title: Introduction
sidebar_position: 1
slug: /intro
---

# Tanuki

**Tanuki** is a declarative Python DSL for procedural geometry that compiles to multiple 3D backends.

Write your 3D models as pure Python functions. Tanuki compiles them into standalone scripts for Blender, OpenSCAD, JSCAD, or OpenCascade.js.

## Key ideas

- **Pure functions** — DSL functions return immutable IR nodes. No global state.
- **Pipe composition** — The `|` operator chains transforms: `cube(1,1,1) | translate(5,0,0) | rotate(0,0,45)`.
- **One graph, many targets** — Compile the same IR graph to any supported backend.
- **Deterministic** — Same inputs always produce the same output.

## Architecture

```
Python DSL  →  Immutable IR graph  →  Backend compiler  →  Output file
```

Three layers:

1. **DSL** (`tanuki.dsl`) — Pure functions (`cube`, `union`, `transform`, …) build an IR tree.
2. **IR** (`tanuki.ir`) — Immutable frozen dataclasses representing the geometry graph.
3. **Backends** (`tanuki.backends`) — Each backend consumes the IR and emits a target-specific source file.

## Quick example

```python
from tanuki.dsl import *
from tanuki.backends import render

def create_bracket():
    with model("bracket") as ctx:
        base = cube(20, 10, 3, "base")
        hole = cylinder(2, 5, "bore") | translate(-6, 0, 0)
        result = difference(base, [hole])
        output(result)
    return ctx.graph

graph = create_bracket()
render(graph, target="blender", mode="script", output_path="bracket.py")
# Run in Blender: blender --background --python bracket.py
```

## Supported backends

| Target | Output | Description |
|--------|--------|-------------|
| `"blender"` | `.py` | Blender Geometry Nodes via `bpy` |
| `"openscad"` | `.scad` | Native OpenSCAD CSG |
| `"jscad"` | `.jscad` | `@jscad/modeling` CommonJS module |
| `"opencascade"` | `.js` | OpenCascade.js BREP ES Module |
