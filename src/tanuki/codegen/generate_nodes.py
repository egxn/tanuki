"""Auto-generate node_map.py from Blender Geometry Nodes JSON metadata.

Reads docs/geometry_nodes_categories/*.json and produces a Python module
with dictionaries mapping node types to their metadata (inputs, outputs, etc.).

Usage::

    python -m tanuki.codegen.generate_nodes
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path


DOCS_DIR = Path(__file__).resolve().parents[3] / "docs" / "geometry_nodes_categories"
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "backends" / "blender" / "node_map.py"


def _load_all_nodes(docs_dir: Path) -> list[dict]:
    """Read every *_nodes.json file and return a flat list of node dicts."""
    nodes: list[dict] = []
    for p in sorted(docs_dir.glob("*_nodes.json")):
        with open(p) as f:
            data = json.load(f)
        nodes.extend(data.get("nodes", []))
    return nodes


def _format_socket(sock: dict) -> str:
    """Format a single socket dict as a Python dict literal."""
    parts = [
        f'"name": {sock["name"]!r}',
        f'"identifier": {sock.get("identifier", sock["name"])!r}',
        f'"type": {sock["type"]!r}',
    ]
    if "default_value" in sock:
        parts.append(f'"default_value": {sock["default_value"]!r}')
    return "{" + ", ".join(parts) + "}"


def _format_node_entry(node: dict) -> str:
    """Format a complete node entry for NODE_REGISTRY."""
    inputs_str = ",\n            ".join(_format_socket(s) for s in node.get("inputs", []))
    outputs_str = ",\n            ".join(_format_socket(s) for s in node.get("outputs", []))
    return textwrap.dedent(f"""\
    {node["type"]!r}: {{
        "name": {node["name"]!r},
        "type": {node["type"]!r},
        "category": {node.get("category", "Other")!r},
        "description": {node.get("description", "")!r},
        "inputs": [
            {inputs_str}
        ],
        "outputs": [
            {outputs_str}
        ],
    }}""")


def generate(docs_dir: Path = DOCS_DIR, output_path: Path = OUTPUT_PATH) -> str:
    """Generate node_map.py content and write it to *output_path*.

    Returns the generated source code.
    """
    nodes = _load_all_nodes(docs_dir)

    # Build NODE_REGISTRY entries
    entries = ",\n".join(f"    {_format_node_entry(n)}" for n in nodes)

    # Build a convenient name→type mapping for the most common DSL primitives
    dsl_map_lines = []
    known_dsl = {
        "cube": "GeometryNodeMeshCube",
        "cylinder": "GeometryNodeMeshCylinder",
        "cone": "GeometryNodeMeshCone",
        "sphere": "GeometryNodeMeshUVSphere",
        "point": "GeometryNodePoints",
        "grid": "GeometryNodeMeshGrid",
        "circle": "GeometryNodeMeshCircle",
        "line": "GeometryNodeMeshLine",
        "ico_sphere": "GeometryNodeMeshIcoSphere",
    }
    for dsl_name, bpy_type in sorted(known_dsl.items()):
        dsl_map_lines.append(f'    {dsl_name!r}: {bpy_type!r},')

    dsl_map_str = "\n".join(dsl_map_lines)

    num_files = len(list(docs_dir.glob("*_nodes.json")))
    source = (
        f'"""Auto-generated Blender Geometry Nodes metadata.\n'
        f"\n"
        f"DO NOT EDIT MANUALLY — regenerate with:\n"
        f"    python -m tanuki.codegen.generate_nodes\n"
        f"\n"
        f"Generated from {len(nodes)} nodes across {num_files} category files.\n"
        f'"""\n'
        f"\n"
        f"# Maps bpy node type string → full metadata (inputs, outputs, etc.)\n"
        f"NODE_REGISTRY: dict[str, dict] = {{\n"
        f"{entries}\n"
        f"}}\n"
        f"\n"
        f"# Convenience: DSL primitive name → bpy node type\n"
        f"DSL_PRIMITIVE_MAP: dict[str, str] = {{\n"
        f"{dsl_map_str}\n"
        f"}}\n"
        f"\n"
        f"# Maps bpy node type → list of input socket dicts\n"
        f"NODE_INPUTS: dict[str, list[dict]] = {{\n"
        f'    bpy_type: info["inputs"] for bpy_type, info in NODE_REGISTRY.items()\n'
        f"}}\n"
        f"\n"
        f"# Maps bpy node type → list of output socket dicts\n"
        f"NODE_OUTPUTS: dict[str, list[dict]] = {{\n"
        f'    bpy_type: info["outputs"] for bpy_type, info in NODE_REGISTRY.items()\n'
        f"}}\n"
        f"\n"
        f"# Maps bpy node type → human-readable name\n"
        f"NODE_NAMES: dict[str, str] = {{\n"
        f'    bpy_type: info["name"] for bpy_type, info in NODE_REGISTRY.items()\n'
        f"}}\n"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(source)
    return source


if __name__ == "__main__":
    src = generate()
    print(f"Generated {OUTPUT_PATH} ({len(src)} bytes, "
          f"{src.count(chr(10))} lines)")
