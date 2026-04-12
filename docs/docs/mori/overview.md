---
id: overview
title: Mori Ecosystem
sidebar_position: 1
---

# Tanuki Mori

**Tanuki Mori** is the ecosystem layer of the Tanuki project.

While the core of Tanuki provides a procedural geometry framework and multi-backend generation system, **Mori** contains domain-specific tools built on top of it.

The name *Mori* (森) means **forest** in Japanese — a natural habitat for tanuki and a metaphor for a growing ecosystem of tools and ideas.

## Purpose

This directory hosts specialised modules that use Tanuki to generate geometry for specific applications:

- **Game development** — procedural map generation, engine-specific geometry pipelines
- **Digital fabrication** — parametric models for 3D printing
- **Papercraft and sculpture** — unfolding 3D meshes into printable templates

Each module can define its own rules, validators, and generators while relying on the core Tanuki geometry system.

## Modules

| Module | Path | Description |
|--------|------|-------------|
| [Halo Maps](./halo-maps) | `mori/halo_maps/` | Procedural Halo CE BSP map generation |
| [Print Labo](./print-labo) | `mori/print_labo/` | Parametric parts for 3D printing |

## Structure

Each module typically contains:

- `generators.py` — geometry generators built on the Tanuki DSL
- `validators.py` — domain-specific constraint validators
- `exporters.py` — pipeline tools for the target format
- `scene.py` — scene/context setup helpers
- A `README.md` with module-specific documentation

## Running Mori modules

```bash
# Combined output (default)
PYTHONPATH=src python -m tanuki.mori.<module>

# One file per part
PYTHONPATH=src python -m tanuki.mori.<module> --mode individual

# Custom output path
PYTHONPATH=src python -m tanuki.mori.<module> --output path/
```
