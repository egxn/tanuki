"""Backend compilers for geometry IR.

Provides a unified ``render()`` function to compile or execute IR graphs.
Accepts a single graph or a sequence of graphs for batch export.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence, Union

from ..ir.graph import IRGraph


def render(
    graph: IRGraph | Sequence[IRGraph],
    target: str = "blender",
    mode: str = "script",
    output_path: str | Path | None = None,
) -> str | Path | list[Path] | None:
    """Render one or more IR graphs to the specified backend.

    Args:
        graph: A single IR graph **or** a sequence of graphs.
            When multiple graphs are given:
            - *script* mode with ``output_path`` ending in ``.py`` uses
              ``combined_export`` (single file, one ``setup_<name>()`` each).
            - *script* mode with a directory path (or no extension) uses
              ``individual_export`` (one file per graph).
        target: Backend target (currently only ``"blender"``).
        mode: ``"script"`` to generate .py file(s), ``"direct"`` to execute via bpy.
        output_path: File or directory path for script mode.

    Returns:
        Single graph + no output_path → source string.
        Single graph + output_path → Path written.
        Multiple graphs + combined → Path written.
        Multiple graphs + individual → list[Path] written.
        Direct mode → None.
    """
    if target != "blender":
        raise ValueError(f"Unsupported target: {target!r}. Currently only 'blender' is supported.")

    # --- multiple graphs ----------------------------------------------------
    if isinstance(graph, (list, tuple)):
        graphs: Sequence[IRGraph] = graph

        if mode == "direct":
            from .blender.runtime import execute
            for g in graphs:
                execute(g)
            return None

        if mode != "script":
            raise ValueError(f"Unsupported mode: {mode!r}. Use 'script' or 'direct'.")

        from ..dsl.export import combined_export, individual_export

        if output_path is None:
            output_path = "output_gen.py"

        p = Path(output_path)
        if p.suffix == ".py":
            return combined_export(graphs, p)
        return individual_export(graphs, p)

    # --- single graph -------------------------------------------------------
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
