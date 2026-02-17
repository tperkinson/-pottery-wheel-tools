#!/usr/bin/env python3
"""Inside-facing slip scraper that composes the reusable saddle."""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from pathlib import Path

ATTACHMENTS_ROOT = Path(__file__).resolve().parents[2]
MOUNT_MODULE_DIR = ATTACHMENTS_ROOT / "saddle" / "v1"
if str(MOUNT_MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MOUNT_MODULE_DIR))

try:
    from saddle_v1 import (
        SaddleParams,
        build_saddle,
        validate_saddle,
    )
except ImportError as exc:
    print(
        "Unable to import saddle component from: "
        f"{MOUNT_MODULE_DIR / 'saddle_v1.py'}",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc

# -------------------------------
# Primary knobs (edit these first)
# -------------------------------
# Forwarded to reusable mount component; fit logic remains in saddle_v1.py.
PRIMARY_PAN_WALL_THICKNESS_MM = 4.5
PRIMARY_FIT_CLEARANCE_MM = 0.5
PRIMARY_CAPTURE_DEPTH_MM = 18.0
PRIMARY_MOUNT_WALL_THICKNESS_MM = 4.0
PRIMARY_MOUNT_HEIGHT_MM = 40.0
PRIMARY_INSIDE_DROP_GAP_MM = 4.5
PRIMARY_INSIDE_DROP_TOP_Z_MM = 26.8
PRIMARY_DETENT_ENABLE = False
PRIMARY_DETENT_HEIGHT_MM = 1.2

PRIMARY_SCRAPER_WIDTH_MM = 75.0
PRIMARY_SCRAPER_REACH_MM = 15.0
PRIMARY_SCRAPER_RISE_MM = 15.0
PRIMARY_SCRAPER_LIP_RADIUS_MM = 14.0
PRIMARY_SCRAPER_DRAIN_GAP_MM = 6.0
PRIMARY_SCRAPER_LIP_SPAN_DEG = 140.0
PRIMARY_SCRAPER_EDGE_RADIUS_MM = 0.8
PRIMARY_SCRAPER_EDGE_ANGLE_DEG = 20.0
PRIMARY_GUSSET_THICKNESS_MM = 5.0
PRIMARY_MATERIAL = "PLA"

try:
    from build123d import (
        Align,
        Axis,
        Box,
        BuildLine,
        BuildPart,
        BuildSketch,
        Locations,
        Plane,
        Polyline,
        add,
        export_stl,
        extrude,
        fillet,
        make_face,
    )
except ImportError as exc:
    print(
        "Missing dependency: build123d. Install with:\n"
        "  python3.13 -m pip install -r cad/build123d/requirements.txt",
        file=sys.stderr,
    )
    print("build123d currently requires Python < 3.14.", file=sys.stderr)
    raise SystemExit(2) from exc


REPO_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_OUTPUT = REPO_ROOT / "build/slip_scraper_inside_v1_b123d.stl"

# -------------------------------
# Run config (same names across scripts)
# -------------------------------
USE_HEAD_CONFIG = False
HEAD_PREVIEW = True
HEAD_EXPORT = False
HEAD_OUTPUT = DEFAULT_OUTPUT
HEAD_MOUNT_ONLY = False


@dataclass(frozen=True)
class SlipScraperInsideParams:
    # -------------------------------
    # Quick Tuning
    # -------------------------------
    pan_wall_thickness: float = PRIMARY_PAN_WALL_THICKNESS_MM
    fit_clearance: float = PRIMARY_FIT_CLEARANCE_MM
    capture_depth: float = PRIMARY_CAPTURE_DEPTH_MM
    mount_wall_thickness: float = PRIMARY_MOUNT_WALL_THICKNESS_MM
    mount_height: float = PRIMARY_MOUNT_HEIGHT_MM
    inside_drop_gap_from_back_wall: float = PRIMARY_INSIDE_DROP_GAP_MM
    inside_drop_top_z: float = PRIMARY_INSIDE_DROP_TOP_Z_MM
    detent_enable: bool = PRIMARY_DETENT_ENABLE
    detent_height: float = PRIMARY_DETENT_HEIGHT_MM

    scraper_width: float = PRIMARY_SCRAPER_WIDTH_MM
    scraper_reach: float = PRIMARY_SCRAPER_REACH_MM
    scraper_rise: float = PRIMARY_SCRAPER_RISE_MM
    scraper_lip_radius: float = PRIMARY_SCRAPER_LIP_RADIUS_MM
    scraper_drain_gap: float = PRIMARY_SCRAPER_DRAIN_GAP_MM
    scraper_lip_span_deg: float = PRIMARY_SCRAPER_LIP_SPAN_DEG
    scraper_edge_radius: float = PRIMARY_SCRAPER_EDGE_RADIUS_MM
    scraper_edge_angle_deg: float = PRIMARY_SCRAPER_EDGE_ANGLE_DEG
    gusset_thickness: float = PRIMARY_GUSSET_THICKNESS_MM
    material: str = PRIMARY_MATERIAL
    mount_only: bool = False

    # -------------------------------
    # Strength / Printability
    # -------------------------------
    scraper_neck_thickness: float = 6.0
    scraper_head_thickness: float = 4.0
    min_recommended_lip_radius: float = 8.0
    min_recommended_drain_gap: float = 3.0
    min_recommended_scraper_thickness: float = 3.0
    min_recommended_gusset_thickness: float = 3.0

    # -------------------------------
    # Advanced Controls
    # -------------------------------
    scraper_y_offset: float = 0.0


@dataclass(frozen=True)
class RuntimeOptions:
    output: Path
    preview: bool
    export: bool
    mount_only: bool


def _mount_params_from_product(params: SlipScraperInsideParams) -> SaddleParams:
    return SaddleParams(
        pan_wall_thickness=params.pan_wall_thickness,
        fit_clearance=params.fit_clearance,
        capture_depth=params.capture_depth,
        mount_wall_thickness=params.mount_wall_thickness,
        mount_height=params.mount_height,
        inside_drop_gap_from_back_wall=params.inside_drop_gap_from_back_wall,
        inside_drop_top_z=params.inside_drop_top_z,
        detent_enable=params.detent_enable,
        detent_height=params.detent_height,
        material=params.material,
    )


def _arc_points_xz(
    cx: float, cz: float, radius: float, start_deg: float, end_deg: float, segments: int
) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for i in range(segments + 1):
        t = i / segments
        angle_deg = start_deg + (end_deg - start_deg) * t
        angle_rad = math.radians(angle_deg)
        points.append((cx + (radius * math.cos(angle_rad)), cz + (radius * math.sin(angle_rad))))
    return points


def _build_lip_profile_xz(
    params: SlipScraperInsideParams,
    x_inside_face: float,
    z_neck: float,
) -> tuple[list[tuple[float, float]], float, float]:
    if params.scraper_lip_radius <= params.scraper_head_thickness + 0.5:
        raise ValueError("scraper_lip_radius must be larger than scraper_head_thickness.")

    center_x = x_inside_face + params.scraper_reach
    center_z = z_neck + params.scraper_rise
    outer_radius = params.scraper_lip_radius
    inner_radius = outer_radius - params.scraper_head_thickness

    target_lip_min_x = x_inside_face + params.scraper_drain_gap
    current_lip_min_x = center_x - outer_radius
    if current_lip_min_x < target_lip_min_x:
        center_x += target_lip_min_x - current_lip_min_x

    half_span = max(20.0, min(85.0, params.scraper_lip_span_deg * 0.5))
    start_deg = 180.0 - half_span
    end_deg = 180.0 + half_span

    outer_points = _arc_points_xz(center_x, center_z, outer_radius, start_deg, end_deg, segments=26)
    inner_points = _arc_points_xz(center_x, center_z, inner_radius, end_deg, start_deg, segments=26)
    return outer_points + inner_points, center_x, center_z


def _build_lip_part(
    params: SlipScraperInsideParams,
    x_inside_face: float,
    y_center: float,
    z_neck: float,
):
    lip_profile, center_x, center_z = _build_lip_profile_xz(params, x_inside_face, z_neck)
    lip_plane = Plane(origin=(0.0, y_center, 0.0), x_dir=(1.0, 0.0, 0.0), z_dir=(0.0, 0.0, 1.0))

    with BuildPart() as lip:
        with BuildSketch(lip_plane) as lip_sketch:
            with BuildLine():
                Polyline(*lip_profile, close=True)
            make_face()
        extrude(lip_sketch.sketch, amount=params.scraper_width, both=True)

        edge_radius = min(
            params.scraper_edge_radius,
            params.scraper_head_thickness * 0.45,
            params.scraper_lip_radius * 0.25,
        )
        if edge_radius > 0:
            try:
                fillet(lip.edges(), edge_radius)
            except ValueError:
                # Keep build robust if a full-edge fillet is over-constrained.
                pass

    lip_part = lip.part
    lip_bb = lip_part.bounding_box()
    return lip_part, lip_bb.min.X, center_x, center_z


def _add_side_support_ribs(
    params: SlipScraperInsideParams,
    mount_bb,
    x_inside_face: float,
    lip_min_x: float,
    lip_center_z: float,
) -> None:
    rib_width = max(4.0, min(params.gusset_thickness, (mount_bb.max.Y - mount_bb.min.Y) * 0.45))
    rib_length = max(2.0, (lip_min_x - x_inside_face) + 1.2)
    rib_height = max(7.0, params.mount_height * 0.20)
    x_center = x_inside_face + (rib_length * 0.5)
    z_center = lip_center_z - (params.scraper_lip_radius * 0.30)

    y_front = mount_bb.min.Y + (rib_width * 0.5)
    y_back = mount_bb.max.Y - (rib_width * 0.5)

    for y_pos in (y_front, y_back):
        with Locations((x_center, y_pos, z_center)):
            Box(
                rib_length,
                rib_width,
                rib_height,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
            )


def build_slip_scraper_inside(params: SlipScraperInsideParams):
    mount_params = _mount_params_from_product(params)
    mount_warnings, mount_errors = validate_saddle(mount_params)
    if mount_errors:
        raise ValueError("Invalid mount parameters: " + " | ".join(mount_errors))

    for warning in mount_warnings:
        print(f"WARN: {warning}", file=sys.stderr)

    if params.scraper_head_thickness < params.min_recommended_scraper_thickness:
        print(
            f"WARN: scraper_head_thickness={params.scraper_head_thickness:.2f} mm may be too thin for durability.",
            file=sys.stderr,
        )
    if params.scraper_lip_radius < params.min_recommended_lip_radius:
        print(
            f"WARN: scraper_lip_radius={params.scraper_lip_radius:.2f} mm may be too small for smooth hand feel.",
            file=sys.stderr,
        )
    if params.scraper_drain_gap < params.min_recommended_drain_gap:
        print(
            f"WARN: scraper_drain_gap={params.scraper_drain_gap:.2f} mm may clog with slip; "
            f"recommended >= {params.min_recommended_drain_gap:.2f} mm.",
            file=sys.stderr,
        )
    if params.gusset_thickness < params.min_recommended_gusset_thickness:
        print(
            f"WARN: gusset_thickness={params.gusset_thickness:.2f} mm may be too thin for reinforcement.",
            file=sys.stderr,
        )

    mount_part = build_saddle(mount_params)
    if params.mount_only:
        return mount_part

    mount_bb = mount_part.bounding_box()
    x_inside_face = mount_bb.max.X
    y_center = ((mount_bb.min.Y + mount_bb.max.Y) / 2.0) + params.scraper_y_offset
    z_neck = mount_params.mount_height * 0.50

    lip_part, lip_min_x, _lip_center_x, lip_center_z = _build_lip_part(
        params,
        x_inside_face,
        y_center,
        z_neck,
    )

    with BuildPart() as assembly:
        add(mount_part)
        add(lip_part)
        _add_side_support_ribs(
            params=params,
            mount_bb=mount_bb,
            x_inside_face=x_inside_face,
            lip_min_x=lip_min_x,
            lip_center_z=lip_center_z,
        )

    return assembly.part.rotate(Axis.X, 0.0)


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
    parser = argparse.ArgumentParser(description="Build inside-facing slip scraper v1")
    parser.add_argument(
        "--output",
        "-o",
        default=str(DEFAULT_OUTPUT),
        help=f"Output STL path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--mount-only",
        action="store_true",
        help="Build only the reusable mount component",
    )
    parser.add_argument(
        "--inside-drop-gap",
        type=float,
        default=PRIMARY_INSIDE_DROP_GAP_MM,
        help=f"Inside wall drop X distance from back wall in mm (default: {PRIMARY_INSIDE_DROP_GAP_MM})",
    )
    parser.add_argument(
        "--inside-drop-top-z",
        type=float,
        default=PRIMARY_INSIDE_DROP_TOP_Z_MM,
        help=f"Top Z for rectangle-style inside drop wall in mm (default: {PRIMARY_INSIDE_DROP_TOP_Z_MM})",
    )
    parser.add_argument(
        "--scraper-reach",
        type=float,
        default=PRIMARY_SCRAPER_REACH_MM,
        help=f"Lip center radial offset from saddle inside wall in mm (default: {PRIMARY_SCRAPER_REACH_MM})",
    )
    parser.add_argument(
        "--scraper-rise",
        type=float,
        default=PRIMARY_SCRAPER_RISE_MM,
        help=f"Lip center vertical rise from neck in mm (default: {PRIMARY_SCRAPER_RISE_MM})",
    )
    parser.add_argument(
        "--lip-radius",
        type=float,
        default=PRIMARY_SCRAPER_LIP_RADIUS_MM,
        help=f"Lip arc radius in mm (default: {PRIMARY_SCRAPER_LIP_RADIUS_MM})",
    )
    parser.add_argument(
        "--drain-gap",
        type=float,
        default=PRIMARY_SCRAPER_DRAIN_GAP_MM,
        help=f"Minimum gap between saddle and lip for runoff in mm (default: {PRIMARY_SCRAPER_DRAIN_GAP_MM})",
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
    return RuntimeOptions(
        output=Path(args.output),
        preview=args.preview,
        export=args.export,
        mount_only=args.mount_only,
    )


def runtime_from_head_config() -> RuntimeOptions:
    return RuntimeOptions(
        output=Path(HEAD_OUTPUT),
        preview=HEAD_PREVIEW,
        export=HEAD_EXPORT,
        mount_only=HEAD_MOUNT_ONLY,
    )


def main() -> int:
    args = parse_args()
    run = runtime_from_head_config() if USE_HEAD_CONFIG else runtime_from_args(args)

    params = SlipScraperInsideParams(
        mount_only=run.mount_only,
        inside_drop_gap_from_back_wall=args.inside_drop_gap,
        inside_drop_top_z=args.inside_drop_top_z,
        scraper_reach=args.scraper_reach,
        scraper_rise=args.scraper_rise,
        scraper_lip_radius=args.lip_radius,
        scraper_drain_gap=args.drain_gap,
    )
    model = build_slip_scraper_inside(params)

    if run.preview:
        preview_part(model)
        if not run.export:
            print("Preview-only mode: STL export skipped.")
            mode = "mount_only" if run.mount_only else "full_assembly"
            print(
                f"mode={mode} reach={params.scraper_reach:.2f}mm rise={params.scraper_rise:.2f}mm "
                f"lip_radius={params.scraper_lip_radius:.2f}mm width={params.scraper_width:.2f}mm"
            )
            return 0

    run.output.parent.mkdir(parents=True, exist_ok=True)
    export_stl(model, str(run.output))
    mode = "mount_only" if run.mount_only else "full_assembly"
    print(f"Exported: {run.output}")
    print(
        f"mode={mode} reach={params.scraper_reach:.2f}mm rise={params.scraper_rise:.2f}mm "
        f"lip_radius={params.scraper_lip_radius:.2f}mm width={params.scraper_width:.2f}mm"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
