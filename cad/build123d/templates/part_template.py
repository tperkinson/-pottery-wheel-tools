#!/usr/bin/env python3
"""Template for new build123d parts in pottery-wheel-tools."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

# -------------------------------
# Primary knobs (edit these first)
# -------------------------------
PRIMARY_TEXT = "PART"
PRIMARY_SCALE_FACTOR = 1.0
PRIMARY_WIDTH_MM = 40.0
PRIMARY_DEPTH_MM = 40.0
PRIMARY_HEIGHT_MM = 20.0

try:
    from build123d import Align, Axis, Box, BuildPart, export_stl
except ImportError as exc:
    print(
        "Missing dependency: build123d. Install with:\n"
        "  python3.13 -m pip install -r cad/build123d/requirements.txt",
        file=sys.stderr,
    )
    print("build123d currently requires Python < 3.14.", file=sys.stderr)
    raise SystemExit(2) from exc


REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_OUTPUT = REPO_ROOT / "build/part_template_b123d.stl"

# -------------------------------
# Run config (same names across scripts)
# -------------------------------
USE_HEAD_CONFIG = False
HEAD_PREVIEW = True
HEAD_EXPORT = False
HEAD_OUTPUT = DEFAULT_OUTPUT


@dataclass(frozen=True)
class PartParams:
    # -------------------------------
    # Quick Tuning
    # -------------------------------
    scale_factor: float = PRIMARY_SCALE_FACTOR
    width: float = PRIMARY_WIDTH_MM
    depth: float = PRIMARY_DEPTH_MM
    height: float = PRIMARY_HEIGHT_MM

    # -------------------------------
    # Strength / Printability
    # -------------------------------
    min_wall: float = 2.0

    # -------------------------------
    # Advanced Controls
    # -------------------------------
    fillet_radius: float = 0.0


@dataclass(frozen=True)
class RuntimeOptions:
    output: Path
    preview: bool
    export: bool


def build_part(params: PartParams):
    with BuildPart() as part:
        Box(
            params.width * params.scale_factor,
            params.depth * params.scale_factor,
            params.height * params.scale_factor,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
    return part.part.rotate(Axis.X, 0.0)


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Template build123d part")
    parser.add_argument(
        "--output",
        "-o",
        default=str(DEFAULT_OUTPUT),
        help=f"Output STL path (default: {DEFAULT_OUTPUT})",
    )
    # VS Code "Run Python File" passes no args; default preview in this path.
    default_preview = len(sys.argv) == 1
    parser.add_argument(
        "--preview",
        action="store_true",
        default=default_preview,
        help="Show preview and skip STL export unless --export is also set",
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="When used with --preview, also export STL",
    )
    return parser.parse_args()


def runtime_from_args(args: argparse.Namespace) -> RuntimeOptions:
    return RuntimeOptions(output=Path(args.output), preview=args.preview, export=args.export)


def runtime_from_head_config() -> RuntimeOptions:
    return RuntimeOptions(output=Path(HEAD_OUTPUT), preview=HEAD_PREVIEW, export=HEAD_EXPORT)


def main() -> int:
    run = runtime_from_head_config() if USE_HEAD_CONFIG else runtime_from_args(parse_args())
    params = PartParams()
    model = build_part(params)

    if run.preview:
        preview_part(model)
        if not run.export:
            print("Preview-only mode: STL export skipped.")
            return 0

    out_path = run.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    export_stl(model, str(out_path))
    print(f"Exported: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
