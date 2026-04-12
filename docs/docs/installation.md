---
id: installation
title: Installation
sidebar_position: 2
---

# Installation

## Requirements

- Python 3.10+
- For the Blender backend: Blender 4.x or 5.x
- For the OpenSCAD backend: [OpenSCAD](https://openscad.org/) (runtime only)
- For the JSCAD backend: Node.js 18+ and `@jscad/modeling`
- For the OpenCascade.js backend: Node.js 18+ and `opencascade.js`

## Install the Python package

```bash
cd src/tanuki
pip install -e ".[dev]"
```

Or without cloning, add to your project directly:

```bash
pip install -e /path/to/tanuki/src/tanuki
```

## Development install

```bash
git clone <repo>
cd tanuki
python -m venv .venv
source .venv/bin/activate
cd src/tanuki && pip install -e ".[dev]"
```

### Run without installing

If you prefer not to install via pip, you can set `PYTHONPATH`:

```bash
PYTHONPATH=src python -c "from tanuki.dsl import *; print('OK')"
```

## Running tests

```bash
# Unit tests (no Blender required)
PYTHONPATH=src python -m pytest src/tanuki/tests/test_compiler.py \
    src/tanuki/tests/test_dsl.py \
    src/tanuki/tests/test_ir.py \
    src/tanuki/tests/test_new_nodes.py -q

# All tests (Blender integration tests may fail without Blender in PATH)
PYTHONPATH=src python -m pytest src/tanuki/tests/ -q
```
