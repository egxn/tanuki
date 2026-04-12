---
id: halo-maps
title: Halo Maps
sidebar_position: 2
---

# Halo CE Maps Module

**Path:** `src/tanuki/mori/halo_maps/`

This module contains tools for generating and validating maps for **Halo: Combat Evolved** using the Tanuki procedural geometry framework.

The goal is to automate parts of the Halo map creation pipeline while enforcing the technical constraints required by the Halo engine and the Halo Editing Kit (HEK).

## Background

Maps in Halo: Combat Evolved are built around a **BSP (Binary Space Partition)** structure that defines the playable world geometry. The BSP is compiled using the Halo Editing Kit tools and later populated with objects such as weapons, vehicles, and spawn points.

This module focuses primarily on generating **valid BSP geometry** and assisting with procedural map layouts.

## Utilities

### `setup_scene`

Configures the Blender scene for Halo CE map development.

- Unit system: Metric, scale 1.0, length in meters
- Creates standard collections: `BSP`, `SCENERY`, `SPAWNS`, `VEHICLES`, `WEAPONS`, `MARKERS`, `COLLISION`, `DEBUG`

### `create_bsp_root_object`

Creates the `bsp_world` mesh object in the `BSP` collection at the origin.

### `initialize_geometry_nodes`

Creates the base Geometry Nodes tree used for procedural map generation.

## Validators

The `validators.py` module enforces Halo CE BSP constraints:

- Polygon count limits
- Geometry must be watertight / manifold
- No T-intersections in the BSP
- Correct scale (Halo uses World Units)

## Generators

The `generators.py` module provides procedural generators for common map elements:

- Corridors and rooms
- Terrain patches
- Spawn rooms
- Weapon / vehicle pads

## Usage

```python
from tanuki.mori.halo_maps import scene, generators, validators

# Set up the Blender scene
scene.setup_scene()

# Generate a simple room
room = generators.create_room(width=20, depth=30, height=6)

# Validate before export
validators.check_bsp(room)

# Export to .blend or Halo geometry format
```
