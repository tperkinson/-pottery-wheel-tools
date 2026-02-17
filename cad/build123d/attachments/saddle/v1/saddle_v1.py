#!/usr/bin/env python3
"""Reusable saddle mount component for inward-facing pottery attachments."""

from __future__ import annotations

import argparse
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# -------------------------------
# Primary knobs (edit these first)
# -------------------------------
PRIMARY_PAN_WALL_THICKNESS_MM = 4.5
PRIMARY_FIT_CLEARANCE_MM = 0.5
PRIMARY_CAPTURE_DEPTH_MM = 18.0
PRIMARY_MOUNT_WALL_THICKNESS_MM = 4.0
PRIMARY_MOUNT_HEIGHT_MM = 40.0
PRIMARY_SWEEP_RADIUS_MM = 222.25
PRIMARY_INSIDE_DROP_GAP_MM = 4.5
PRIMARY_INSIDE_DROP_TOP_Z_MM = 26.8
PRIMARY_INSIDE_TOP_SQUARE_ENABLE = True
PRIMARY_INSIDE_TOP_SQUARE_WIDTH_MM = 4.0
PRIMARY_OUTSIDE_TOP_RELIEF_ENABLE = True
PRIMARY_OUTSIDE_TOP_RELIEF_WIDTH_MM = 8.0
PRIMARY_OUTSIDE_TOP_RELIEF_DEPTH_MM = 4.0
PRIMARY_DETENT_ENABLE = False
PRIMARY_DETENT_HEIGHT_MM = 1.2
PRIMARY_MATERIAL = "PLA"

# Measured from core_mount_system/c_clamp/v1/c_clamp_profile_topref_v1.scad
CANONICAL_C_CLAMP_TOP_SPAN_MM = 13.0363
CANONICAL_C_CLAMP_MOUTH_GAP_MM = 5.4901

try:
    from build123d import (
        Axis,
        BuildLine,
        BuildPart,
        BuildSketch,
        Plane,
        Polyline,
        Mode,
        add,
        export_stl,
        make_face,
        revolve,
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
CORE_PROFILE_SCAD = REPO_ROOT / "core_mount_system/c_clamp/v1/c_clamp_profile_topref_v1.scad"
DEFAULT_OUTPUT = REPO_ROOT / "build/saddle_v1_b123d.stl"

# -------------------------------
# Run config (same names across scripts)
# -------------------------------
USE_HEAD_CONFIG = False
HEAD_PREVIEW = True
HEAD_EXPORT = False
HEAD_OUTPUT = DEFAULT_OUTPUT


@dataclass(frozen=True)
class CClampProfile:
    min_profile_x: float
    max_profile_x: float
    min_profile_y: float
    max_profile_y: float
    points: list[tuple[float, float]]


@dataclass(frozen=True)
class SaddleParams:
    # -------------------------------
    # Quick Tuning
    # -------------------------------
    pan_wall_thickness: float = PRIMARY_PAN_WALL_THICKNESS_MM
    fit_clearance: float = PRIMARY_FIT_CLEARANCE_MM
    capture_depth: float = PRIMARY_CAPTURE_DEPTH_MM
    mount_wall_thickness: float = PRIMARY_MOUNT_WALL_THICKNESS_MM
    mount_height: float = PRIMARY_MOUNT_HEIGHT_MM
    sweep_radius: float = PRIMARY_SWEEP_RADIUS_MM
    inside_drop_gap_from_back_wall: float = PRIMARY_INSIDE_DROP_GAP_MM
    inside_drop_top_z: float = PRIMARY_INSIDE_DROP_TOP_Z_MM
    inside_top_square_enable: bool = PRIMARY_INSIDE_TOP_SQUARE_ENABLE
    inside_top_square_width: float = PRIMARY_INSIDE_TOP_SQUARE_WIDTH_MM
    outside_top_relief_enable: bool = PRIMARY_OUTSIDE_TOP_RELIEF_ENABLE
    outside_top_relief_width: float = PRIMARY_OUTSIDE_TOP_RELIEF_WIDTH_MM
    outside_top_relief_depth: float = PRIMARY_OUTSIDE_TOP_RELIEF_DEPTH_MM
    detent_enable: bool = PRIMARY_DETENT_ENABLE
    detent_height: float = PRIMARY_DETENT_HEIGHT_MM
    material: str = PRIMARY_MATERIAL

    # -------------------------------
    # Strength / Printability
    # -------------------------------
    detent_length: float = 4.0
    min_recommended_wall: float = 2.0
    min_recommended_clearance: float = 0.25
    max_recommended_clearance: float = 0.9

    # -------------------------------
    # Advanced Controls
    # -------------------------------
    canonical_profile_path: Path = CORE_PROFILE_SCAD


@dataclass(frozen=True)
class RuntimeOptions:
    output: Path
    preview: bool
    export: bool


def _parse_scalar(text: str, name: str) -> float:
    match = re.search(rf"^\s*{re.escape(name)}\s*=\s*([-+]?\d*\.?\d+)\s*;", text, re.MULTILINE)
    if not match:
        raise ValueError(f"Missing scalar in profile file: {name}")
    return float(match.group(1))


def _canonical_back_wall_bottom_y(profile: CClampProfile) -> float:
    tol = 1e-5
    wall_ys = [y for (x, y) in profile.points if abs(x - profile.max_profile_x) <= tol]
    if not wall_ys:
        raise ValueError("Could not find canonical back-wall points at max_profile_x.")
    return min(wall_ys)


def _canonical_back_wall_bottom_index(profile: CClampProfile) -> int:
    target_x = profile.max_profile_x
    target_y = _canonical_back_wall_bottom_y(profile)
    return min(
        range(len(profile.points)),
        key=lambda i: abs(profile.points[i][0] - target_x) + abs(profile.points[i][1] - target_y),
    )


def _canonical_top_front_indices(profile: CClampProfile) -> tuple[int, int]:
    top_idx = None
    for i, (x, y) in enumerate(profile.points):
        if abs(x) <= 1e-6 and abs(y) <= 1e-6:
            top_idx = i
            break
    if top_idx is None:
        raise ValueError("Could not find canonical top-front point (0,0) in C-clamp profile.")

    raw = profile.points
    for i in range(top_idx + 1, len(raw)):
        x, y = raw[i]
        if i + 1 < len(raw):
            x_next, y_next = raw[i + 1]
            # Start of canonical near-vertical branch on the inner side.
            if abs(x_next - x) <= 1e-4 and y <= -10.0 and y_next < y:
                return top_idx, i

    raise ValueError("Canonical top-front segment extraction failed.")


def _canonical_top_front_segment(profile: CClampProfile) -> list[tuple[float, float]]:
    top_idx, top_end_idx = _canonical_top_front_indices(profile)
    segment = profile.points[top_idx : top_end_idx + 1]
    if len(segment) < 3:
        raise ValueError("Canonical top-front segment extraction failed.")
    return segment


def _canonical_lower_wrap_segment(profile: CClampProfile) -> list[tuple[float, float]]:
    back_bottom_idx = _canonical_back_wall_bottom_index(profile)
    _, top_end_idx = _canonical_top_front_indices(profile)
    start_idx = top_end_idx + 1
    if start_idx >= len(profile.points):
        raise ValueError("Canonical lower-wrap extraction failed.")

    # Inner-right branch down through lower tip and back to outside back-wall base.
    segment = profile.points[start_idx:] + profile.points[: back_bottom_idx + 1]
    if len(segment) < 3:
        raise ValueError("Canonical lower-wrap extraction failed.")
    return segment


def load_c_clamp_profile(path: Path = CORE_PROFILE_SCAD) -> CClampProfile:
    text = path.read_text(encoding="utf-8")
    points_match = re.search(r"profile_points\s*=\s*\[(.*?)\];", text, re.DOTALL)
    if not points_match:
        raise ValueError(f"Missing profile_points array in {path}")

    point_pairs = re.findall(r"\[\s*([-+]?\d*\.?\d+)\s*,\s*([-+]?\d*\.?\d+)\s*\]", points_match.group(1))
    points = [(float(x), float(y)) for x, y in point_pairs]
    if not points:
        raise ValueError(f"No points parsed from profile_points in {path}")

    return CClampProfile(
        min_profile_x=_parse_scalar(text, "min_profile_x"),
        max_profile_x=_parse_scalar(text, "max_profile_x"),
        min_profile_y=_parse_scalar(text, "min_profile_y"),
        max_profile_y=_parse_scalar(text, "max_profile_y"),
        points=points,
    )


def mount_throat_width(params: SaddleParams) -> float:
    return params.pan_wall_thickness + (2.0 * params.fit_clearance)


def c_curve_target_gap(params: SaddleParams) -> float:
    # Horizontal gap from lower outside contact to straight inside wall.
    return params.inside_drop_gap_from_back_wall


def sweep_angle_deg(params: SaddleParams) -> float:
    return math.degrees(params.capture_depth / params.sweep_radius)


def validate_saddle(params: SaddleParams) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    errors: list[str] = []

    if params.pan_wall_thickness <= 0:
        errors.append("pan_wall_thickness must be > 0 mm")
    if params.fit_clearance < 0:
        errors.append("fit_clearance must be >= 0 mm")
    if params.capture_depth <= 0:
        errors.append("capture_depth must be > 0 mm")
    if params.sweep_radius <= 0:
        errors.append("sweep_radius must be > 0 mm")
    if params.mount_height <= 0:
        errors.append("mount_height must be > 0 mm")
    if params.mount_wall_thickness <= 0:
        errors.append("mount_wall_thickness must be > 0 mm")
    if params.inside_drop_gap_from_back_wall <= 0:
        errors.append("inside_drop_gap_from_back_wall must be > 0 mm")
    if params.inside_drop_top_z <= 0:
        errors.append("inside_drop_top_z must be > 0 mm")
    if params.inside_drop_top_z >= params.mount_height:
        errors.append("inside_drop_top_z must be < mount_height")
    if params.inside_top_square_width <= 0:
        errors.append("inside_top_square_width must be > 0 mm")
    if params.outside_top_relief_width <= 0:
        errors.append("outside_top_relief_width must be > 0 mm")
    if params.outside_top_relief_depth <= 0:
        errors.append("outside_top_relief_depth must be > 0 mm")
    if params.outside_top_relief_depth >= params.mount_height:
        errors.append("outside_top_relief_depth must be < mount_height")

    if params.fit_clearance < params.min_recommended_clearance:
        warnings.append(
            f"clearance looks tight ({params.fit_clearance:.2f} mm). "
            f"Recommended >= {params.min_recommended_clearance:.2f} mm."
        )
    if params.fit_clearance > params.max_recommended_clearance:
        warnings.append(
            f"clearance looks loose ({params.fit_clearance:.2f} mm). "
            f"Recommended <= {params.max_recommended_clearance:.2f} mm."
        )

    if params.mount_wall_thickness < params.min_recommended_wall:
        warnings.append(
            f"mount_wall_thickness={params.mount_wall_thickness:.2f} mm may be too thin for reliable prints."
        )

    if params.detent_enable and params.detent_height <= 0:
        warnings.append("detent is enabled but detent_height <= 0; detent will be ineffective.")

    return warnings, errors


def _x_intersection_on_polyline(
    points: list[tuple[float, float]],
    target_x: float,
    *,
    from_end: bool = False,
) -> tuple[int, tuple[float, float]]:
    index_iter = range(len(points) - 1, 0, -1) if from_end else range(1, len(points))
    for i in index_iter:
        x0, z0 = points[i - 1]
        x1, z1 = points[i]
        if (x0 <= target_x <= x1) or (x0 >= target_x >= x1):
            if abs(x1 - x0) < 1e-9:
                return i, (target_x, z1)
            t = (target_x - x0) / (x1 - x0)
            return i, (target_x, z0 + (z1 - z0) * t)
    raise ValueError(f"Could not intersect polyline with x={target_x:.3f} mm.")


def _build_mount_profiles(
    profile: CClampProfile, params: SaddleParams
) -> tuple[
    list[tuple[float, float]],
    list[tuple[float, float]],
    list[tuple[float, float]] | None,
    list[tuple[float, float]] | None,
]:
    back_bottom = _canonical_back_wall_bottom_y(profile)
    back_height = profile.max_profile_y - back_bottom
    if back_height <= 0:
        raise ValueError("Invalid canonical back-wall height.")

    z_scale = params.mount_height / back_height
    x_scale = params.mount_wall_thickness / PRIMARY_MOUNT_WALL_THICKNESS_MM
    top_z = params.mount_height

    raw_curve = _canonical_top_front_segment(profile)
    raw_lower_wrap = _canonical_lower_wrap_segment(profile)
    transformed_curve = [((profile.max_profile_x - x) * x_scale, top_z + (y * z_scale)) for (x, y) in raw_curve]
    transformed_lower_wrap = [((profile.max_profile_x - x) * x_scale, top_z + (y * z_scale)) for (x, y) in raw_lower_wrap]
    canonical_profile = [((profile.max_profile_x - x) * x_scale, top_z + (y * z_scale)) for (x, y) in profile.points]

    # Rectangle-style right drop wall measured from the outer/right side.
    outer_right_x = max(p[0] for p in canonical_profile)
    if params.inside_drop_gap_from_back_wall >= outer_right_x:
        raise ValueError(
            "invalid throat geometry: inside_drop_gap_from_back_wall is too large for canonical profile."
        )
    x_inner = outer_right_x - params.inside_drop_gap_from_back_wall

    # Keep the drop contiguous: start no lower than the canonical top-curve contact,
    # but allow raising it with the parameter to create a longer straight inside wall.
    _, (_, drop_z_auto) = _x_intersection_on_polyline(transformed_curve, x_inner, from_end=True)
    z_top = max(drop_z_auto, params.inside_drop_top_z)

    z_bottom = min(z for _, z in canonical_profile)
    if z_top <= z_bottom + 0.5:
        raise ValueError("invalid throat geometry: drop rectangle has no positive height.")

    rectangle_profile = [
        (x_inner, z_bottom),
        (outer_right_x, z_bottom),
        (outer_right_x, z_top),
        (x_inner, z_top),
    ]

    top_square_profile: list[tuple[float, float]] | None = None
    if params.inside_top_square_enable and z_top < (top_z - 0.25):
        x_cap_left = max(x_inner, outer_right_x - params.inside_top_square_width)
        if x_cap_left >= outer_right_x - 0.1:
            raise ValueError("inside_top_square_width is too small for printable top cap.")
        top_square_profile = [
            (x_cap_left, z_top),
            (outer_right_x, z_top),
            (outer_right_x, top_z),
            (x_cap_left, top_z),
        ]

    outside_relief_profile: list[tuple[float, float]] | None = None
    if params.outside_top_relief_enable:
        top_flat_span_scaled = CANONICAL_C_CLAMP_TOP_SPAN_MM * x_scale
        relief_width = min(params.outside_top_relief_width, max(0.5, top_flat_span_scaled - 0.4))
        relief_bottom_z = top_z - params.outside_top_relief_depth
        if relief_width > 0.5 and relief_bottom_z < top_z - 0.2:
            # Remove non-structural square mass on the outside top via a wedge cut.
            outside_relief_profile = [
                (0.0, top_z),
                (relief_width, top_z),
                (0.0, relief_bottom_z),
            ]

    return canonical_profile, rectangle_profile, top_square_profile, outside_relief_profile


def _sweep_closed_profile(points_xz: list[tuple[float, float]], params: SaddleParams):
    sweep_angle = sweep_angle_deg(params)
    shifted = [(x + params.sweep_radius, z) for (x, z) in points_xz]

    with BuildPart() as part:
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Polyline(*shifted, close=True)
            make_face()
        revolve(axis=Axis.Z, revolution_arc=sweep_angle)

    return part.part.translate((-params.sweep_radius, 0.0, 0.0))


def build_saddle(params: SaddleParams):
    """Build saddle from canonical C-clamp profile plus parameterized right rectangle drop wall."""
    _, errors = validate_saddle(params)
    if errors:
        raise ValueError("Invalid saddle parameters: " + " | ".join(errors))

    profile = load_c_clamp_profile(params.canonical_profile_path)
    canonical_profile, rectangle_profile, top_square_profile, outside_relief_profile = _build_mount_profiles(
        profile, params
    )
    canonical_part = _sweep_closed_profile(canonical_profile, params)
    rectangle_part = _sweep_closed_profile(rectangle_profile, params)
    with BuildPart() as fused:
        add(canonical_part)
        add(rectangle_part)
        if top_square_profile is not None:
            add(_sweep_closed_profile(top_square_profile, params))
        if outside_relief_profile is not None:
            add(_sweep_closed_profile(outside_relief_profile, params), mode=Mode.SUBTRACT)
    return fused.part.rotate(Axis.X, 0.0)


def bottom_horizontal_gap_mm(params: SaddleParams) -> float:
    return params.inside_drop_gap_from_back_wall


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
    parser = argparse.ArgumentParser(description="Build saddle v1")
    parser.add_argument(
        "--output",
        "-o",
        default=str(DEFAULT_OUTPUT),
        help=f"Output STL path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--pan-wall-thickness",
        type=float,
        default=PRIMARY_PAN_WALL_THICKNESS_MM,
        help=f"Splash-pan wall thickness in mm (default: {PRIMARY_PAN_WALL_THICKNESS_MM})",
    )
    parser.add_argument(
        "--clearance",
        type=float,
        default=PRIMARY_FIT_CLEARANCE_MM,
        help=f"Per-side fit clearance in mm (default: {PRIMARY_FIT_CLEARANCE_MM})",
    )
    parser.add_argument(
        "--inside-drop-gap",
        type=float,
        default=PRIMARY_INSIDE_DROP_GAP_MM,
        help=f"Inside drop wall gap from lower outside touch in mm (default: {PRIMARY_INSIDE_DROP_GAP_MM})",
    )
    parser.add_argument(
        "--inside-drop-top-z",
        type=float,
        default=PRIMARY_INSIDE_DROP_TOP_Z_MM,
        help=(
            "Target Z for straight-drop start (effective Z is max(canonical_contact_z, this value))."
        ),
    )
    parser.add_argument(
        "--inside-top-square",
        action=argparse.BooleanOptionalAction,
        default=PRIMARY_INSIDE_TOP_SQUARE_ENABLE,
        help="Enable/disable square top cap on the inside drop wall (default: enabled).",
    )
    parser.add_argument(
        "--inside-top-square-width",
        type=float,
        default=PRIMARY_INSIDE_TOP_SQUARE_WIDTH_MM,
        help=f"Inside square top cap width in mm (default: {PRIMARY_INSIDE_TOP_SQUARE_WIDTH_MM})",
    )
    parser.add_argument(
        "--outside-top-relief",
        action=argparse.BooleanOptionalAction,
        default=PRIMARY_OUTSIDE_TOP_RELIEF_ENABLE,
        help="Enable/disable outside top material relief cut (default: enabled).",
    )
    parser.add_argument(
        "--outside-top-relief-width",
        type=float,
        default=PRIMARY_OUTSIDE_TOP_RELIEF_WIDTH_MM,
        help=f"Outside top relief width in mm (default: {PRIMARY_OUTSIDE_TOP_RELIEF_WIDTH_MM})",
    )
    parser.add_argument(
        "--outside-top-relief-depth",
        type=float,
        default=PRIMARY_OUTSIDE_TOP_RELIEF_DEPTH_MM,
        help=f"Outside top relief depth in mm (default: {PRIMARY_OUTSIDE_TOP_RELIEF_DEPTH_MM})",
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
    )


def runtime_from_head_config() -> RuntimeOptions:
    return RuntimeOptions(
        output=Path(HEAD_OUTPUT),
        preview=HEAD_PREVIEW,
        export=HEAD_EXPORT,
    )


def main() -> int:
    args = parse_args()
    run = runtime_from_head_config() if USE_HEAD_CONFIG else runtime_from_args(args)

    params = SaddleParams(
        pan_wall_thickness=args.pan_wall_thickness,
        fit_clearance=args.clearance,
        inside_drop_gap_from_back_wall=args.inside_drop_gap,
        inside_drop_top_z=args.inside_drop_top_z,
        inside_top_square_enable=args.inside_top_square,
        inside_top_square_width=args.inside_top_square_width,
        outside_top_relief_enable=args.outside_top_relief,
        outside_top_relief_width=args.outside_top_relief_width,
        outside_top_relief_depth=args.outside_top_relief_depth,
    )

    warnings, errors = validate_saddle(params)
    for warning in warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2

    mount = build_saddle(params)

    if run.preview:
        preview_part(mount)
        if not run.export:
            print("Preview-only mode: STL export skipped.")
            bottom_gap = bottom_horizontal_gap_mm(params)
            print(
                f"mode=canonical_drop_profile throat={mount_throat_width(params):.2f}mm "
                f"drop_gap={c_curve_target_gap(params):.2f}mm "
                f"bottom_gap={bottom_gap:.2f}mm "
                f"drop_top_z={params.inside_drop_top_z:.2f}mm "
                f"inside_top_square={'on' if params.inside_top_square_enable else 'off'} "
                f"inside_top_square_width={params.inside_top_square_width:.2f}mm "
                f"outside_top_relief={'on' if params.outside_top_relief_enable else 'off'} "
                f"outside_top_relief_w={params.outside_top_relief_width:.2f}mm "
                f"outside_top_relief_d={params.outside_top_relief_depth:.2f}mm "
                f"depth={params.capture_depth:.2f}mm "
                f"sweep_angle={sweep_angle_deg(params):.3f}deg"
            )
            return 0

    run.output.parent.mkdir(parents=True, exist_ok=True)
    export_stl(mount, str(run.output))
    bottom_gap = bottom_horizontal_gap_mm(params)
    print(f"Exported: {run.output}")
    print(
        f"mode=canonical_drop_profile throat={mount_throat_width(params):.2f}mm "
        f"drop_gap={c_curve_target_gap(params):.2f}mm "
        f"bottom_gap={bottom_gap:.2f}mm "
        f"drop_top_z={params.inside_drop_top_z:.2f}mm "
        f"inside_top_square={'on' if params.inside_top_square_enable else 'off'} "
        f"inside_top_square_width={params.inside_top_square_width:.2f}mm "
        f"outside_top_relief={'on' if params.outside_top_relief_enable else 'off'} "
        f"outside_top_relief_w={params.outside_top_relief_width:.2f}mm "
        f"outside_top_relief_d={params.outside_top_relief_depth:.2f}mm "
        f"depth={params.capture_depth:.2f}mm "
        f"sweep_angle={sweep_angle_deg(params):.3f}deg"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
