---
applyTo: "src/tanuki/mori/**"
---

# Mori — Real-World Model Library

`src/tanuki/mori/` contains production models built with the Tanuki DSL.

## Sub-libraries

| Folder | Description |
|--------|-------------|
| `print_labo/` | Camera & darkroom equipment (film scanners, lens boards, trays, …) |
| `halo_maps/` | Parametric 3D map generation from SVG/GeoJSON sources |
| `paper/` | Paper-craft and origami-related geometry |

---

## print_labo — conventions

### File naming

Files are numbered for assembly order: `01_dev_tank.py`, `02_tube_cap.py`, `03_spinner.py`, …  
Unnumbered files are standalone parts: `bellows_cog.py`, `tray.py`, `lens_machine.py`, …

### Module structure

Every `print_labo` file follows this pattern:

```python
from tanuki.dsl import *

# 1. Module-level constants (clearances, dimensions)
clearance = 0.125

# 2. One factory function per part
def create_<part_name>() -> IRGraph:
    with model("<part_name>") as ctx:
        base = cube(w, d, h, "base")
        # ... geometry ...
        output(result)
    return ctx.graph

# 3. ALL_PARTS list — used by the exporter
ALL_PARTS = [
    create_part_a(),
    create_part_b(),
]

# 4. __main__ block — CLI runner
if __name__ == "__main__":
    import argparse
    from tanuki.dsl.export import combined_export, individual_export

    parser = argparse.ArgumentParser(description="Compile")
    parser.add_argument("--mode", choices=["combined", "individual"], default="combined")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    if args.mode == "combined":
        out = args.output or "<model_name>.py"
        path = combined_export(ALL_PARTS, out)
        print(f"Generated {len(ALL_PARTS)} parts in {path} ({path.stat().st_size // 1024} KB)")
    else:
        out = args.output or "<model_name>_gen"
        written = individual_export(ALL_PARTS, out)
        print(f"Generated {len(written)} files in {out}/")
```

### Running a model

```bash
# Generate combined .py file (default)
PYTHONPATH=src python -m tanuki.mori.print_labo.lens_machine

# Generate individual files per part
PYTHONPATH=src python -m tanuki.mori.print_labo.lens_machine --mode individual

# Custom output path
PYTHONPATH=src python -m tanuki.mori.print_labo.lens_machine --output my_out.py
```

### Dimensional conventions

- All dimensions are in **millimetres** (1 unit = 1 mm in Blender)
- `clearance` constants (typically `0.1`–`0.2`) are defined at module level and subtracted from tight-fitting parts
- Axis convention: `cube(X, Y, Z)` → width, depth, height
- `cylinder(radius, depth)` extends along the Z axis by default
- `place(x, y, z)` is a semantic alias for `translate` — use it for positioning parts relative to an assembly origin

### Typical part patterns

**Simple box with hollow interior:**
```python
outer = cube(w, d, h)
inner = cube(w - wall*2, d - wall*2, h)
box   = difference(outer, [inner])
```

**Cylinder with axial hole:**
```python
body = cylinder(r_outer, depth)
hole = cylinder(r_inner, depth)
part = difference(body, [hole])
```

**Stacked / offset cutouts:**
```python
result = difference(base, [
    cutout_a | place(0, 0, 0),
    cutout_b | place(offset_x, 0, 0),
    cutout_c | place(offset_x * 2, 0, 0),
])
```

**Multi-part assembly export:**
```python
ALL_PARTS = [
    create_body(),
    create_lid(),
    create_knob(),
]
combined_export(ALL_PARTS, "assembly.py")
```

### Common mistakes to avoid

- **Missing comma in `difference()` list** — every element in the cutter list needs a trailing comma when placing on a new line:
  ```python
  # WRONG — missing comma after first place call
  result = difference(base, [
      cutter | place(0, 0, 0)
      cutter | place(10, 0, 0)   # ← SyntaxError
  ])

  # CORRECT
  result = difference(base, [
      cutter | place(0, 0, 0),
      cutter | place(10, 0, 0),
  ])
  ```
- **Modifying IR nodes** — IR nodes are frozen; never reassign a field. Build a new node instead.
- **Forgetting `output()`** — `model()` will raise if no `output()` is called before the context exits.
