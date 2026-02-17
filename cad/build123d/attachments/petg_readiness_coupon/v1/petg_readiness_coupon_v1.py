#!/usr/bin/env python3
"""Fast PETG readiness coupon for preflight checks before long prints."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

# -------------------------------
# Primary knobs (edit these first)
# -------------------------------
PRIMARY_BASE_WIDTH_MM = 72.0
PRIMARY_BASE_DEPTH_MM = 42.0
PRIMARY_BASE_THICKNESS_MM = 2.2
PRIMARY_FEATURE_HEIGHT_MM = 18.0
PRIMARY_BRIDGE_SPAN_MM = 18.0
PRIMARY_STRINGING_GAP_MM = 46.0
PRIMARY_THIN_WALLS_MM = (0.8, 1.2, 1.6)

try:
    from build123d import Align, Axis, Box, BuildPart, Cylinder, Locations, Mode, export_stl
except ImportError as exc:
    print(
        "Missing dependency: build123d. Install with:\n"
        "  python3.13 -m pip install -r cad/build123d/requirements.txt",
        file=sys.stderr,
    )
    print("build123d currently requires Python < 3.14.", file=sys.stderr)
    raise SystemExit(2) from exc


REPO_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_OUTPUT = REPO_ROOT / "build/petg_readiness_coupon_v1_b123d.stl"

# -------------------------------
# Run config (same names across scripts)
# -------------------------------
USE_HEAD_CONFIG = False
HEAD_PREVIEW = True
HEAD_EXPORT = False
HEAD_OUTPUT = DEFAULT_OUTPUT


@dataclass(frozen=True)
class PetgReadinessCouponParams:
    # -------------------------------
    # Quick Tuning
    # -------------------------------
    base_width: float = PRIMARY_BASE_WIDTH_MM
    base_depth: float = PRIMARY_BASE_DEPTH_MM
    base_thickness: float = PRIMARY_BASE_THICKNESS_MM
    feature_height: float = PRIMARY_FEATURE_HEIGHT_MM
    bridge_span: float = PRIMARY_BRIDGE_SPAN_MM
    stringing_gap: float = PRIMARY_STRINGING_GAP_MM
    thin_wall_thicknesses: tuple[float, float, float] = tuple(PRIMARY_THIN_WALLS_MM)

    # -------------------------------
    # Strength / Printability
    # -------------------------------
    bridge_roof_thickness: float = 1.0
    bridge_side_wall: float = 4.0
    tower_diameter: float = 5.0
    overhang_step_rise: float = 0.8
    overhang_step_run: float = 1.0
    overhang_step_count: int = 10

    # -------------------------------
    # Advanced Controls
    # -------------------------------
    bridge_block_depth: float = 16.0
    thin_wall_length: float = 16.0
    thin_wall_pitch: float = 5.0
    tower_edge_margin: float = 6.0


@dataclass(frozen=True)
class RuntimeOptions:
    output: Path
    preview: bool
    export: bool


def validate_coupon(params: PetgReadinessCouponParams) -> None:
    if params.base_width <= 0 or params.base_depth <= 0 or params.base_thickness <= 0:
        raise ValueError("Base dimensions must be > 0.")
    if params.feature_height <= 0:
        raise ValueError("feature_height must be > 0.")
    if params.bridge_span <= 0:
        raise ValueError("bridge_span must be > 0.")
    if params.bridge_roof_thickness <= 0:
        raise ValueError("bridge_roof_thickness must be > 0.")
    if params.bridge_side_wall <= 0:
        raise ValueError("bridge_side_wall must be > 0.")
    if params.tower_diameter <= 0:
        raise ValueError("tower_diameter must be > 0.")
    if params.stringing_gap <= 0:
        raise ValueError("stringing_gap must be > 0.")
    if params.overhang_step_count <= 0:
        raise ValueError("overhang_step_count must be > 0.")
    if params.overhang_step_rise <= 0 or params.overhang_step_run <= 0:
        raise ValueError("overhang_step_rise and overhang_step_run must be > 0.")
    if not params.thin_wall_thicknesses:
        raise ValueError("thin_wall_thicknesses must not be empty.")
    if any(thickness <= 0 for thickness in params.thin_wall_thicknesses):
        raise ValueError("All thin wall thicknesses must be > 0.")

    bridge_block_width = params.bridge_span + (2.0 * params.bridge_side_wall)
    if bridge_block_width >= params.base_width - 6.0:
        raise ValueError("bridge span + side walls is too wide for the chosen base width.")

    tower_span = params.stringing_gap + params.tower_diameter
    if tower_span >= params.base_width - 4.0:
        raise ValueError("stringing_gap and tower_diameter are too large for the base width.")


def build_petg_readiness_coupon(params: PetgReadinessCouponParams):
    validate_coupon(params)

    bridge_block_width = params.bridge_span + (2.0 * params.bridge_side_wall)
    bridge_slot_height = params.feature_height - params.bridge_roof_thickness

    overhang_anchor_width = 8.0
    overhang_anchor_depth = 8.0
    overhang_stack_height = params.overhang_step_count * params.overhang_step_rise

    with BuildPart() as coupon:
        Box(
            params.base_width,
            params.base_depth,
            params.base_thickness,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

        tower_y = (params.base_depth * 0.5) - params.tower_edge_margin
        tower_x = params.stringing_gap * 0.5
        with Locations(
            (tower_x, tower_y, params.base_thickness),
            (-tower_x, tower_y, params.base_thickness),
        ):
            Cylinder(
                radius=params.tower_diameter * 0.5,
                height=params.feature_height,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        bridge_y = -(params.base_depth * 0.18)
        with Locations((0.0, bridge_y, params.base_thickness)):
            Box(
                bridge_block_width,
                params.bridge_block_depth,
                params.feature_height,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            Box(
                params.bridge_span,
                params.bridge_block_depth + 2.0,
                bridge_slot_height,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

        overhang_x = -(params.base_width * 0.42)
        overhang_y = -(params.base_depth * 0.40)
        with Locations((overhang_x, overhang_y, params.base_thickness)):
            Box(
                overhang_anchor_width,
                overhang_anchor_depth,
                overhang_stack_height,
                align=(Align.MIN, Align.MIN, Align.MIN),
            )

        for idx in range(params.overhang_step_count):
            z0 = params.base_thickness + (idx * params.overhang_step_rise)
            y0 = overhang_y + overhang_anchor_depth + (idx * params.overhang_step_run)
            with Locations((overhang_x, y0, z0)):
                Box(
                    overhang_anchor_width,
                    params.overhang_step_run,
                    params.overhang_step_rise,
                    align=(Align.MIN, Align.MIN, Align.MIN),
                )

        thin_wall_x0 = params.base_width * 0.24
        thin_wall_y = -(params.base_depth * 0.34)
        for idx, wall_t in enumerate(params.thin_wall_thicknesses):
            x = thin_wall_x0 + (idx * params.thin_wall_pitch)
            with Locations((x, thin_wall_y, params.base_thickness)):
                Box(
                    wall_t,
                    params.thin_wall_length,
                    params.feature_height * 0.75,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )

    return coupon.part.rotate(Axis.X, 0.0)


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
    parser = argparse.ArgumentParser(
        description="Fast PETG readiness coupon for bridge/stringing/overhang checks"
    )
    parser.add_argument(
        "--output",
        "-o",
        default=str(DEFAULT_OUTPUT),
        help=f"Output STL path (default: {DEFAULT_OUTPUT})",
    )
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
    params = PetgReadinessCouponParams()
    model = build_petg_readiness_coupon(params)

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
