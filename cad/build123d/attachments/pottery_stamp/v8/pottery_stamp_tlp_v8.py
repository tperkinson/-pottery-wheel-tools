#!/usr/bin/env python3
"""build123d port of attachments/pottery_stamp/v8/pottery_stamp_tlp_v8.scad."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

# -------------------------------
# Primary knobs (edit these first)
# -------------------------------
PRIMARY_TEXT = "TLP"
PRIMARY_FONT = "Arial"
PRIMARY_SCALE_FACTOR = 0.6

PRIMARY_STAMP_BASE_DIAMETER_MM = 38.0
PRIMARY_TEXT_BASE_SIZE_MM = 13.0
PRIMARY_BASE_THICKNESS_MM = 6.0
PRIMARY_LETTER_HEIGHT_MM = 2.8

PRIMARY_HANDLE_NECK_DIAMETER_MM = 14.0
PRIMARY_HANDLE_HEAD_DIAMETER_MM = 30.0
PRIMARY_HANDLE_HEIGHT_MM = 22.0

# VS Code one-click run behavior (no CLI args):
# False -> preview only
# True  -> preview + STL export
PRIMARY_EXPORT_ON_RUN = False

try:
    from build123d import (
        Align,
        Axis,
        Box,
        BuildPart,
        BuildSketch,
        Cone,
        Cylinder,
        FontStyle,
        Locations,
        Mode,
        Plane,
        Text,
        export_stl,
        extrude,
    )
except ImportError as exc:
    print(
        "Missing dependency: build123d. Install with:\n"
        "  python3.13 -m pip install -r cad/build123d/requirements.txt",
        file=sys.stderr,
    )
    print(
        "build123d currently requires Python < 3.14.",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


@dataclass(frozen=True)
class StampParams:
    scale_factor: float = PRIMARY_SCALE_FACTOR
    base_thickness: float = PRIMARY_BASE_THICKNESS_MM
    letter_height: float = PRIMARY_LETTER_HEIGHT_MM
    handle_base_d: float = PRIMARY_HANDLE_NECK_DIAMETER_MM
    handle_top_d: float = PRIMARY_HANDLE_HEAD_DIAMETER_MM
    handle_height: float = PRIMARY_HANDLE_HEIGHT_MM
    base_diameter: float = PRIMARY_STAMP_BASE_DIAMETER_MM
    text_base_size: float = PRIMARY_TEXT_BASE_SIZE_MM
    alignment_flat_depth: float = 2.0
    base_alignment_flat_depth: float = 1.4
    text: str = PRIMARY_TEXT
    font: str = PRIMARY_FONT

    @property
    def stamp_diameter(self) -> float:
        return self.base_diameter * self.scale_factor

    @property
    def text_size(self) -> float:
        return self.text_base_size * self.scale_factor


def build_stamp(params: StampParams):
    """Create the stamp solid with the same dimensions/orientation as the v8 SCAD model."""
    with BuildPart() as stamp:
        _add_base_disk(params)
        _add_stamp_text(params)
        _add_mushroom_handle(params)
    # Match OpenSCAD export orientation: text side down on default STL import.
    return stamp.part.rotate(Axis.X, 180)


def _add_base_disk(params: StampParams) -> None:
    base_main_h = params.base_thickness - 0.6

    Cylinder(
        radius=params.stamp_diameter / 2.0,
        height=base_main_h,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    with Locations((0.0, 0.0, base_main_h)):
        Cone(
            bottom_radius=params.stamp_diameter / 2.0,
            top_radius=(params.stamp_diameter - 1.2) / 2.0,
            height=0.6,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

    if params.base_alignment_flat_depth > 0:
        with Locations(
            (
                0.0,
                -params.stamp_diameter / 2.0 + params.base_alignment_flat_depth / 2.0,
                params.base_thickness / 2.0,
            )
        ):
            Box(
                params.stamp_diameter * 1.2,
                params.base_alignment_flat_depth,
                params.base_thickness + 0.2,
                mode=Mode.SUBTRACT,
            )


def _add_stamp_text(params: StampParams) -> None:
    # Mirror on X to preserve stamp impression orientation.
    text_plane = Plane(origin=(0.0, 0.0, 0.15), x_dir=(-1.0, 0.0, 0.0), z_dir=(0.0, 0.0, -1.0))

    with BuildSketch(text_plane) as text_sketch:
        Text(
            txt=params.text,
            font_size=params.text_size,
            font=params.font,
            font_style=FontStyle.BOLD,
            align=(Align.CENTER, Align.CENTER),
        )

    extrude(text_sketch.sketch, amount=params.letter_height)


def _add_mushroom_handle(params: StampParams) -> None:
    with Locations((0.0, 0.0, params.base_thickness)):
        Cone(
            bottom_radius=params.handle_base_d / 2.0,
            top_radius=params.handle_top_d / 2.0,
            height=params.handle_height,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

    if params.alignment_flat_depth > 0:
        with Locations(
            (
                0.0,
                -params.handle_top_d / 2.0 + params.alignment_flat_depth / 2.0,
                params.base_thickness + params.handle_height / 2.0,
            )
        ):
            Box(
                params.handle_top_d * 1.2,
                params.alignment_flat_depth,
                params.handle_height + 0.2,
                mode=Mode.SUBTRACT,
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export pottery stamp TLP v8 STL using build123d.")
    parser.add_argument(
        "--output",
        "-o",
        default="build/pottery_stamp_tlp_v8_b123d.stl",
        help="Output STL path (default: build/pottery_stamp_tlp_v8_b123d.stl)",
    )
    parser.add_argument("--text", default=PRIMARY_TEXT, help=f"Stamp text (default: {PRIMARY_TEXT})")
    parser.add_argument("--font", default=PRIMARY_FONT, help=f"Font family (default: {PRIMARY_FONT})")
    parser.add_argument(
        "--scale-factor",
        type=float,
        default=PRIMARY_SCALE_FACTOR,
        help=f"Global scale factor for stamp diameter and text size (default: {PRIMARY_SCALE_FACTOR})",
    )
    # VS Code "Run Python File" passes no args; default that path to preview for fast iteration.
    no_cli_args = len(sys.argv) == 1
    default_preview = no_cli_args
    default_export = no_cli_args and PRIMARY_EXPORT_ON_RUN
    parser.add_argument(
        "--preview",
        action="store_true",
        default=default_preview,
        help="Show live preview in VS Code OCP Viewer and skip STL export unless --export is also set",
    )
    parser.add_argument(
        "--export",
        action="store_true",
        default=default_export,
        help="When used with --preview, also export STL",
    )
    return parser.parse_args()


def preview_part(part) -> None:
    try:
        from ocp_vscode import show
    except ImportError as exc:
        print(
            "Missing dependency: ocp_vscode. Install with:\n"
            "  python3.13 -m pip install -r cad/build123d/requirements.txt",
            file=sys.stderr,
        )
        raise SystemExit(2) from exc

    show(part)
    print("Preview sent to OCP CAD Viewer.")


def main() -> int:
    args = parse_args()
    params = StampParams(text=args.text, scale_factor=args.scale_factor, font=args.font)
    part = build_stamp(params)

    if args.preview:
        preview_part(part)
        if not args.export:
            print("Preview-only mode: STL export skipped.")
            print(f"stamp_diameter={params.stamp_diameter:.2f}mm text_size={params.text_size:.2f}mm")
            return 0

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    export_stl(part, str(out_path))

    print(f"Exported: {out_path}")
    print(f"stamp_diameter={params.stamp_diameter:.2f}mm text_size={params.text_size:.2f}mm")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
