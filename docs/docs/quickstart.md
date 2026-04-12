---
id: quickstart
title: Quickstart
sidebar_position: 3
---

# Quickstart

## Your first model

Every Tanuki script follows the same pattern:

1. Open a `model()` context manager.
2. Build geometry using DSL functions.
3. Call `output()` to mark the root node.
4. Call `render()` to compile to a target.

```python
from tanuki.dsl import *
from tanuki.backends import render

with model("belt_holder") as ctx:
    base  = cylinder(5.5, 15, "base")
    hole  = cylinder(4.5, 15, "hole")
    part  = difference(base, [hole])
    output(part)

render(ctx.graph, target="blender", mode="script", output_path="belt_holder.py")
```

Run the generated script in Blender:

```bash
blender --background --python belt_holder.py
```

## Using the pipe operator

Transforms can be chained with `|`:

```python
from tanuki.dsl import *
from tanuki.backends import render

with model("tower") as ctx:
    base   = cube(10, 10, 2)
    pillar = cylinder(1.5, 8)  | translate(0, 0, 5)
    cap    = sphere(2)         | translate(0, 0, 10)
    part   = join([base, pillar, cap]) | scale_by(2, 2, 2)
    output(part)

print(render(ctx.graph, target="openscad"))
```

Output:

```scad
scale([2.0, 2.0, 2.0])
  union() {
    translate([-5.0, -5.0, -1.0])
      cube([10, 10, 2]);
    translate([0, 0, 5])
      translate([0.0, 0.0, -4.0])
        cylinder(r=1.5, h=8, $fn=32);
    translate([0, 0, 10])
      sphere(r=2);
  }
```

## Rendering to different backends

The `render()` call is the only thing that changes between targets:

```python
graph = ctx.graph

render(graph, target="blender",      output_path="model.py")
render(graph, target="openscad",     output_path="model.scad")
render(graph, target="jscad",        output_path="model.jscad")
render(graph, target="opencascade",  output_path="model.js")
```

## Multiple models in one file

Pass a list of graphs to write them all at once:

```python
render([graph_a, graph_b], target="openscad", output_path="combined.scad")

# Or write each to a directory
render([graph_a, graph_b], target="openscad", output_path="out/")
```

## Next steps

- [DSL Reference](./dsl/overview) — all primitives, operations, and transforms
- [Backends](./backends/overview) — what each backend supports
- [IR Reference](./ir/overview) — the intermediate representation layer
