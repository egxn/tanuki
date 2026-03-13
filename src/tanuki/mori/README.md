# Tanuki Mori

**Tanuki Mori** is the ecosystem layer of the **Tanuki** project.

While the core of Tanuki provides a procedural geometry framework and multi-backend generation system, **Mori** contains domain-specific tools built on top of it.

The name *Mori* (森) means **forest** in Japanese — a natural habitat for tanuki and a metaphor for a growing ecosystem of tools and ideas.

## Purpose

This directory hosts specialized modules that use Tanuki to generate geometry for specific applications.

Examples include:

* **Game development**

  * Procedural map generation
  * Engine-specific geometry pipelines

* **Digital fabrication**

  * Parametric models for 3D printing

* **Papercraft and sculpture**

  * Unfolding 3D meshes into printable templates
  * Generating edge lengths and fold angles for physical construction

Each module can define its own rules, validators, and generators while relying on the core Tanuki geometry system.

## Structure

Example structure:

```
mori/
   halo_maps_ce/
   fab/
```

Each module typically contains:

* manifest files describing the module and its dependencies
* geometry generators
* domain-specific constraints
* exporters or pipeline tools


## Philosophy

Tanuki Mori is meant to grow organically:
a collection of practical ecosystems built around procedural geometry.
