"""Backend compilers for geometry IR.

Provides a unified ``render()`` function to compile or execute IR graphs.
"""

from __future__ import annotations

from pathlib import Path

from ..ir.graph import IRGraph


def render(
    graph: IRGraph,
    target: str = "blender",
    mode: str = "script",
    output_path: str | Path | None = None,
) -> str | Path | None:
    """Render an IR graph to the specified backend.

    Args:
        graph: The IR graph to render.
        target: Backend target (currently only ``"blender"``).
        mode: ``"script"`` to generate a .py file, ``"direct"`` to execute via bpy.
        output_path: File path for script mode. Defaults to ``{graph.name}.py``.

    Returns:
        For script mode: the generated source string (or Path if output_path given).
        For direct mode: None (side-effects via bpy).
    """
    if target != "blender":
        raise ValueError(f"Unsupported target: {target!r}. Currently only 'blender' is supported.")

    if mode == "script":
        from .blender.compiler import compile_to_source, compile_to_script

        if output_path is not None:
            return compile_to_script(graph, output_path)
        return compile_to_source(graph)

    if mode == "direct":
        from .blender.runtime import execute  # noqa: F811

        execute(graph)
        return None

    raise ValueError(f"Unsupported mode: {mode!r}. Use 'script' or 'direct'.")
