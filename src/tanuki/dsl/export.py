"""Export utilities for compiling Tanuki models to Blender scripts.

Provides two export modes and integrates with ``render()``:
- **combined_export**: all graphs compiled into a single .py file,
  each with its own ``setup_<name>()`` function.
- **individual_export**: each graph compiled into its own .py file
  inside a directory.

Both accept either pre-built ``IRGraph`` objects or zero-argument
callables that return an ``IRGraph``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Sequence, Union

from ..ir.graph import IRGraph

GraphOrFactory = Union[IRGraph, Callable[[], IRGraph]]


def _resolve(item: GraphOrFactory) -> IRGraph:
    """Return an IRGraph, calling the factory if needed."""
    return item() if callable(item) else item


def _extract_setup_body(source: str, func_name: str) -> str:
    """Extract the setup function from compiled source and rename it."""
    lines = source.splitlines()
    out: list[str] = []
    inside = False
    for line in lines:
        if line.startswith("def setup("):
            out.append(line.replace("def setup(", f"def {func_name}("))
            inside = True
        elif inside:
            if line.startswith("# Execute") or line.strip() == "setup()":
                continue
            out.append(line)
    return "\n".join(out)


def combined_export(
    graphs: Sequence[GraphOrFactory],
    output_path: str | Path,
) -> Path:
    """Compile multiple graphs into a single Blender script.

    Each graph's ``setup()`` is renamed to ``setup_<graph.name>()``.
    A single ``import bpy`` heads the file and all setup calls are
    appended at the bottom.

    Returns the path written to.
    """
    from ..backends.blender.compiler import compile_to_source

    output_path = Path(output_path)
    compiled: list[tuple[str, str]] = []

    for item in graphs:
        graph = _resolve(item)
        src = compile_to_source(graph)
        func_name = f"setup_{graph.name}"
        body = _extract_setup_body(src, func_name)
        compiled.append((graph.name, body))

    sections = ["import bpy", "", ""]
    for _name, body in compiled:
        sections.append(body)
        sections.append("")

    sections.append("")
    sections.append("# Execute all parts")
    for name, _ in compiled:
        sections.append(f"setup_{name}()")
    sections.append("")

    output_path.write_text("\n".join(sections))
    return output_path


def individual_export(
    graphs: Sequence[GraphOrFactory],
    output_dir: str | Path,
) -> list[Path]:
    """Compile each graph into its own Blender script file.

    Files are written as ``<output_dir>/<graph.name>.py``.

    Returns the list of paths written.
    """
    from ..backends.blender.compiler import compile_to_source

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for item in graphs:
        graph = _resolve(item)
        src = compile_to_source(graph)
        dest = output_dir / f"{graph.name}.py"
        dest.write_text(src)
        written.append(dest)

    return written
