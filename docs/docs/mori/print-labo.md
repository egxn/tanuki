---
id: print-labo
title: Print Labo
sidebar_position: 3
---

# Print Labo Module

**Path:** `src/tanuki/mori/print_labo/`

Print Labo contains parametric 3D-printable parts built with the Tanuki DSL. Each file is a standalone model generator that outputs a `.py` Blender script (or `.scad` / `.jscad`).

## Models

| File | Description |
|------|-------------|
| `claw.py` | Claw mechanism with sprocket instancing |
| `dslr_scanner_setup.py` | DSLR scanner frame and holder assembly |
| `film_spooler.py` | Film spooler reel mechanism |
| `lamp_parts.py` | Lamp bracket parts |
| `lens_machine.py` | Lens alignment machine parts |
| `minolta_tap.py` | Minolta tap adapter |
| `mogura_exposimeter.py` | Mogura exposimeter housing |

## Running a model

```bash
# Generate a Blender script for the claw
PYTHONPATH=src python -m tanuki.mori.print_labo.claw

# Generate OpenSCAD output
PYTHONPATH=src python -m tanuki.mori.print_labo.claw --target openscad

# Write individual parts to separate files
PYTHONPATH=src python -m tanuki.mori.print_labo.claw --mode individual --output out/
```

## Example — Claw model

```python
from tanuki.dsl import *
from tanuki.backends import render

def create_claw():
    with model("claw") as ctx:
        leg_l = cube(5.5, 50, 2, "leg_l", position=(14.75, 0, 0))
        leg_r = cube(5.5, 50, 2, "leg_r", position=(-14.75, 0, 0))
        top   = cube(35, 10, 2, "top",    position=(0, 25, 0))

        hook   = cylinder(12, 2, "hook",   position=(0, 35, 0))
        h_hole = cylinder(8,  2, "h_hole", position=(0, 35, 0))
        hook   = difference(hook, [h_hole])

        sprocket  = cube(2.5, 1.8, 3, "sprocket", position=(0, 0, 1))
        positions = [(x, y, 0) for y in range(9) for x in [14, -14]]
        sprockets = clones(sprocket, positions)

        result = union([leg_l, leg_r, top, hook, sprockets])
        output(result)
    return ctx.graph

render(create_claw(), target="blender", output_path="claw_gen.py")
```
