"""Command-line entry point for the Stencil Lab.

    python -m tanuki.mori.stencil_lab photo.jpg -o photo.svg --method cmyk --cell 6
    python -m tanuki.mori.stencil_lab photo.jpg -f blender --extrude 0.5
    python -m tanuki.mori.stencil_lab photo.jpg -f dxf --registration target
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .export import (
    write_blender_script,
    write_dxf,
    write_pdf,
    write_png,
    write_stl,
    write_svg,
)
from .fabrication import StencilMask, analyze_cuttability
from .patterns import PATTERN_NAMES
from .pipeline import halftone_stencil
from .registration import add_registration_marks, split_to_plates
from .sizing import PAPER, fit_to_physical, tile_to_paper
from .tiling import tile_stencil

_SUFFIX = {"svg": ".svg", "blender": ".py", "png": ".png",
           "dxf": ".dxf", "pdf": ".pdf", "stl": ".stl"}


def _write(fmt: str, stencil, out: Path, args) -> None:
    if fmt == "svg":
        write_svg(stencil, out, background=args.background)
    elif fmt == "blender":
        write_blender_script(stencil, out, scale=args.scale,
                             extrude=args.extrude, fill=not args.no_fill)
    elif fmt == "png":
        write_png(stencil, out)
    elif fmt == "dxf":
        write_dxf(stencil, out)
    elif fmt == "pdf":
        write_pdf(stencil, out)
    elif fmt == "stl":
        write_stl(stencil, out, thickness=args.thickness, scale=args.scale)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="stencil_lab",
        description="Turn an image into a layered stencil (SVG / PNG / DXF / PDF / STL / Blender).",
    )
    parser.add_argument("image", help="input image (jpg/png/tiff)")
    parser.add_argument("-o", "--output", default=None, help="output path")
    parser.add_argument("-f", "--format", default="svg",
                        choices=list(_SUFFIX), help="output format")
    parser.add_argument("--method", default="cmyk",
                        choices=["cmyk", "rgb", "grayscale", "duotone", "tritone"],
                        help="colour separation method")
    parser.add_argument("--pattern", default="dots", choices=list(PATTERN_NAMES),
                        help="pattern screen to apply")
    parser.add_argument("--cell", type=float, default=8.0, help="pattern cell/spacing (px)")
    parser.add_argument("--carrier", action="store_true",
                        help="use the pattern as a threshold carrier (cut = threshold ∩ pattern)")
    parser.add_argument("--threshold", type=float, default=0.5,
                        help="[carrier] cut where ink coverage ≥ this")
    parser.add_argument("--duty", type=float, default=0.5,
                        help="[carrier] pattern density (0–1); leaves the rest as bridges")
    parser.add_argument("--max-side", type=int, default=1000, help="downscale longest side to N px")
    parser.add_argument("--registration", default=None,
                        choices=["crosshair", "target", "corner"],
                        help="add registration marks of this kind to every layer")
    parser.add_argument("--background", default=None, help="[svg] background colour")
    parser.add_argument("--scale", type=float, default=0.01, help="[blender/stl] units per pixel")
    parser.add_argument("--extrude", type=float, default=0.0, help="[blender] solid half-thickness")
    parser.add_argument("--no-fill", action="store_true", help="[blender] leave curves unfilled")
    parser.add_argument("--thickness", type=float, default=1.0, help="[stl] extrusion thickness")
    parser.add_argument("--tile", default=None, metavar="WxH",
                        help="split into plotter-bed tiles of this pixel size, e.g. 600x800")
    parser.add_argument("--tile-overlap", type=float, default=0.0,
                        help="shared margin between tiles (px)")
    # physical size / printing on sheets
    parser.add_argument("--width-mm", type=float, default=None,
                        help="scale output to this physical width (mm); height by aspect")
    parser.add_argument("--paper", default=None, choices=sorted(PAPER),
                        help="split the (physical) design across sheets of this size")
    parser.add_argument("--landscape", action="store_true", help="[paper] rotate the sheet")
    parser.add_argument("--paper-margin", type=float, default=10.0,
                        help="[paper] unprintable margin per side (mm)")
    parser.add_argument("--paper-overlap", type=float, default=10.0,
                        help="[paper] shared overlap between sheets (mm)")
    parser.add_argument("--analyze", action="store_true",
                        help="report whether the stencil cuts without losing information")
    parser.add_argument("--no-optimize", action="store_true",
                        help="skip cut-optimization; output the raw artistic pattern")
    parser.add_argument("--min-feature", type=float, default=2.0,
                        help="minimum cuttable feature size (px) — analyze & optimize")
    parser.add_argument("--bridge-width", type=float, default=2.0,
                        help="[optimize] width of island-rescue bridges (px)")
    args = parser.parse_args(argv)

    stencil = halftone_stencil(
        args.image, method=args.method, pattern=args.pattern,
        cell=args.cell, max_side=args.max_side,
        optimize=not args.no_optimize, carrier=args.carrier,
        threshold=args.threshold, duty=args.duty,
        min_feature_px=args.min_feature, bridge_width=args.bridge_width,
    )
    if args.registration:
        add_registration_marks(stencil, kind=args.registration)

    if args.analyze:
        report = analyze_cuttability(
            StencilMask.from_stencil(stencil), min_feature_px=args.min_feature,
        )
        print(report)
        return 0 if report.cuttable else 1

    out = (Path(args.output) if args.output
           else Path(args.image).with_suffix(_SUFFIX[args.format]))

    # physical sizing: scale to a real width (mm). A bare --paper fits one sheet.
    if args.width_mm:
        stencil = fit_to_physical(stencil, width_mm=args.width_mm)
    elif args.paper:
        from .sizing import printable_area
        bw, _ = printable_area(args.paper, landscape=args.landscape,
                               margin_mm=args.paper_margin)
        stencil = fit_to_physical(stencil, width_mm=bw)

    if args.paper:
        # one set of sheets per plate — each colour is cut on its own sheet
        plates = (split_to_plates(stencil, with_marks=False)
                  if len(stencil.layers) > 1 else [stencil])
        n = 0
        for plate in plates:
            name = plate.layers[0].name if plate.layers else "plate"
            for tile in tile_to_paper(plate, args.paper, landscape=args.landscape,
                                      margin_mm=args.paper_margin,
                                      overlap_mm=args.paper_overlap):
                tpath = out.with_name(f"{out.stem}_{name}_{tile.name}{out.suffix}")
                _write(args.format, tile.stencil, tpath, args)
                n += 1
        print(
            f"Wrote {n} {args.paper.upper()} sheets ({args.format}, "
            f"{len(plates)} plate(s)) for a "
            f"{stencil.width:.0f}×{stencil.height:.0f} mm design → "
            f"{out.stem}_<plate>_r#c#{out.suffix}"
        )
        return 0

    if args.tile:
        try:
            bw, bh = (float(v) for v in args.tile.lower().split("x"))
        except ValueError:
            parser.error("--tile must look like WIDTHxHEIGHT, e.g. 600x800")
        tiles = tile_stencil(stencil, bw, bh, overlap=args.tile_overlap)
        for tile in tiles:
            tpath = out.with_name(f"{out.stem}_{tile.name}{out.suffix}")
            _write(args.format, tile.stencil, tpath, args)
        print(
            f"Wrote {len(tiles)} tiles ({args.format}) for a "
            f"{int(stencil.width)}×{int(stencil.height)} canvas on a "
            f"{int(bw)}×{int(bh)} bed → {out.stem}_r#c#{out.suffix}"
        )
        return 0

    _write(args.format, stencil, out, args)
    mode = "raw pattern" if args.no_optimize else "cut-optimized"
    print(
        f"Wrote {out} ({args.format}, {mode}) — {len(stencil.layers)} layer(s), "
        f"{stencil.primitive_count} primitives "
        f"({int(stencil.width)}×{int(stencil.height)} {stencil.units})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
