#!/usr/bin/env python3
"""Parameterized C-clamp sweep in build123d using canonical profile as baseline."""

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
PRIMARY_SWEEP_ANGLE_DEG = 24.0
PRIMARY_RADIUS_MM = 222.25
PRIMARY_PROFILE_WIDTH_MM = 27.077  # canonical width (~max_profile_x - min_profile_x)
PRIMARY_BACK_WALL_HEIGHT_MM = 45.398  # canonical straight-wall span (~0 - -45.3977)
PRIMARY_PROFILE_RADIAL_OFFSET_MM = 0.0
PRIMARY_MOUTH_RELIEF_MM = 0.0
PRIMARY_PAD_LENGTH_MM = 13.5
PRIMARY_ATTACHMENT_SUPPORT_ENABLED = True

try:
    from build123d import (
        Axis,
        BuildLine,
        BuildPart,
        BuildSketch,
        Plane,
        Polyline,
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
DEFAULT_OUTPUT = REPO_ROOT / "build/c_clamp_v1_b123d.stl"

# -------------------------------
# Run config (same names across scripts)
# -------------------------------
USE_HEAD_CONFIG = False
HEAD_PREVIEW = True
HEAD_EXPORT = False
HEAD_OUTPUT = DEFAULT_OUTPUT


@dataclass(frozen=True)
class RuntimeOptions:
    output: Path
    preview: bool
    export: bool
    profile_width: float
    back_wall_height: float
    mouth_relief: float
    profile_radial_offset: float
    radius: float
    sweep_angle: float
    pad_length: float
    attachment_support: bool


@dataclass(frozen=True)
class CClampProfile:
    min_profile_x: float
    max_profile_x: float
    min_profile_y: float
    max_profile_y: float
    hook_center_x: float
    points: list[tuple[float, float]]


@dataclass(frozen=True)
class CClampParams:
    # -------------------------------
    # Quick Tuning
    # -------------------------------
    show_clamp: bool = True
    show_pad: bool = True
    enable_attachment_support: bool = PRIMARY_ATTACHMENT_SUPPORT_ENABLED

    sweep_angle: float = PRIMARY_SWEEP_ANGLE_DEG
    radius: float = PRIMARY_RADIUS_MM
    radius_ref_mode: str = "hook_center"  # "hook_center" or "outer_edge"
    axis_z: float = 0.0

    profile_width_target: float = PRIMARY_PROFILE_WIDTH_MM
    back_wall_height_target: float = PRIMARY_BACK_WALL_HEIGHT_MM
    profile_radial_offset: float = PRIMARY_PROFILE_RADIAL_OFFSET_MM
    profile_vertical_offset: float = 0.0

    # Localized widening of the opening-side, near the top of the profile.
    mouth_relief: float = PRIMARY_MOUTH_RELIEF_MM
    mouth_zone_height: float = 14.0
    mouth_zone_x_fraction: float = 0.55

    pad_length: float = PRIMARY_PAD_LENGTH_MM
    pad_thickness: float = 5.0
    pad_overlap: float = 1.0
    pad_offset_y: float = 0.0

    # -------------------------------
    # Strength / Printability
    # -------------------------------
    max_projection: float = 127.0
    ender3_v3_bed_x: float = 220.0
    ender3_v3_bed_y: float = 220.0

    # -------------------------------
    # Advanced Controls
    # -------------------------------
    min_profile_width_recommended: float = 20.0
    min_back_wall_height_recommended: float = 30.0


@dataclass(frozen=True)
class Derived:
    base_width: float
    base_height: float
    base_back_wall_height: float
    base_back_wall_mid_y: float
    back_wall_delta: float
    scale_x: float

    transformed_points: list[tuple[float, float]]
    transformed_min_x: float
    transformed_max_x: float
    transformed_min_y: float
    transformed_max_y: float
    hook_center_x_transformed: float

    radius_ref_x: float
    axis_x: float
    axis_shift_x: float
    mount_outer_radius: float
    pad_outer_radius: float
    sweep_chord_estimate: float
    sweep_arc_estimate: float


def _parse_scalar(text: str, name: str) -> float:
    match = re.search(rf"^\s*{re.escape(name)}\s*=\s*([-+]?\d*\.?\d+)\s*;", text, re.MULTILINE)
    if not match:
        raise ValueError(f"Missing scalar in profile file: {name}")
    return float(match.group(1))


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
        hook_center_x=_parse_scalar(text, "hook_center_x"),
        points=points,
    )


def _canonical_back_wall_bottom_y(profile: CClampProfile) -> float:
    # The long straight wall lives at max_profile_x in the canonical profile.
    tol = 1e-5
    wall_ys = [y for (x, y) in profile.points if abs(x - profile.max_profile_x) <= tol]
    if not wall_ys:
        raise ValueError("Could not find canonical back-wall points at max_profile_x.")
    return min(wall_ys)


def _apply_profile_transform(
    profile: CClampProfile, params: CClampParams
) -> tuple[list[tuple[float, float]], float, float, float, float, float, float, float, float]:
    base_width = profile.max_profile_x - profile.min_profile_x
    base_height = profile.max_profile_y - profile.min_profile_y
    if base_width <= 0 or base_height <= 0:
        raise ValueError("Invalid canonical profile extents.")

    scale_x = params.profile_width_target / base_width
    base_back_wall_bottom_y = _canonical_back_wall_bottom_y(profile)
    base_back_wall_height = profile.max_profile_y - base_back_wall_bottom_y
    base_back_wall_mid_y = (profile.max_profile_y + base_back_wall_bottom_y) * 0.5
    back_wall_delta = params.back_wall_height_target - base_back_wall_height

    # Preserve top-reference and outer-edge intent during scaling.
    anchor_x = profile.max_profile_x
    anchor_y = profile.max_profile_y

    mouth_zone_height = max(0.1, params.mouth_zone_height)
    upper_shift = back_wall_delta * 0.5
    lower_shift = -back_wall_delta * 0.5
    mouth_y_cut = anchor_y + params.profile_vertical_offset + upper_shift - mouth_zone_height
    mouth_x_gate_raw = profile.min_profile_x + base_width * params.mouth_zone_x_fraction

    transformed: list[tuple[float, float]] = []
    for raw_x, raw_y in profile.points:
        x = anchor_x + (raw_x - anchor_x) * scale_x
        # Height tuning: insert/remove length in the middle of the long back wall.
        # This preserves upper/lower curve shapes and moves them apart/together.
        y = raw_y + (upper_shift if raw_y >= base_back_wall_mid_y else lower_shift)

        if params.mouth_relief != 0.0 and raw_x >= mouth_x_gate_raw and y >= mouth_y_cut:
            t = (y - mouth_y_cut) / max(1e-6, (anchor_y - mouth_y_cut))
            t = max(0.0, min(1.0, t))
            x += params.mouth_relief * t

        x += params.profile_radial_offset
        y += params.profile_vertical_offset
        transformed.append((x, y))

    xs = [p[0] for p in transformed]
    ys = [p[1] for p in transformed]

    hook_center_x_transformed = anchor_x + (profile.hook_center_x - anchor_x) * scale_x
    if params.mouth_relief != 0.0 and profile.hook_center_x >= mouth_x_gate_raw:
        hook_center_x_transformed += params.mouth_relief
    hook_center_x_transformed += params.profile_radial_offset

    return (
        transformed,
        min(xs),
        max(xs),
        min(ys),
        max(ys),
        hook_center_x_transformed,
        scale_x,
        base_back_wall_height,
        base_back_wall_mid_y,
        back_wall_delta,
    )


def derive(params: CClampParams, profile: CClampProfile) -> Derived:
    (
        transformed_points,
        transformed_min_x,
        transformed_max_x,
        transformed_min_y,
        transformed_max_y,
        hook_center_x_transformed,
        scale_x,
        base_back_wall_height,
        base_back_wall_mid_y,
        back_wall_delta,
    ) = _apply_profile_transform(profile, params)

    base_width = profile.max_profile_x - profile.min_profile_x
    base_height = profile.max_profile_y - profile.min_profile_y

    radius_ref_x = hook_center_x_transformed if params.radius_ref_mode == "hook_center" else transformed_max_x
    axis_x = radius_ref_x - params.radius
    axis_shift_x = max(0.0, axis_x - transformed_min_x + 0.1)

    mount_outer_radius = axis_shift_x + (transformed_max_x - axis_x)
    pad_length_eff = params.pad_length if (params.show_pad and params.enable_attachment_support) else 0.0
    pad_outer_radius = mount_outer_radius + pad_length_eff

    sweep_rad = math.radians(max(0.0, params.sweep_angle))
    sweep_chord_estimate = 2.0 * pad_outer_radius * math.sin(sweep_rad / 2.0)
    sweep_arc_estimate = pad_outer_radius * sweep_rad

    return Derived(
        base_width=base_width,
        base_height=base_height,
        base_back_wall_height=base_back_wall_height,
        base_back_wall_mid_y=base_back_wall_mid_y,
        back_wall_delta=back_wall_delta,
        scale_x=scale_x,
        transformed_points=transformed_points,
        transformed_min_x=transformed_min_x,
        transformed_max_x=transformed_max_x,
        transformed_min_y=transformed_min_y,
        transformed_max_y=transformed_max_y,
        hook_center_x_transformed=hook_center_x_transformed,
        radius_ref_x=radius_ref_x,
        axis_x=axis_x,
        axis_shift_x=axis_shift_x,
        mount_outer_radius=mount_outer_radius,
        pad_outer_radius=pad_outer_radius,
        sweep_chord_estimate=sweep_chord_estimate,
        sweep_arc_estimate=sweep_arc_estimate,
    )


def _revolve_closed_profile(points_xz: list[tuple[float, float]], sweep_angle: float, start_angle: float = 0.0):
    with BuildPart() as part:
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Polyline(*points_xz, close=True)
            make_face()
        revolve(axis=Axis.Z, revolution_arc=sweep_angle)
    solid = part.part
    if abs(start_angle) > 1e-9:
        solid = solid.rotate(Axis.Z, start_angle)
    return solid


def build_c_clamp_sweep(params: CClampParams, derived: Derived):
    parts = []
    x_shift = derived.axis_shift_x - derived.axis_x
    z_shift = -params.axis_z

    if params.show_clamp:
        clamp_profile_xz = [(x + x_shift, y + z_shift) for (x, y) in derived.transformed_points]
        parts.append(_revolve_closed_profile(clamp_profile_xz, params.sweep_angle))

    if params.show_pad and params.enable_attachment_support and params.pad_length > 0:
        x0 = derived.transformed_max_x - params.pad_overlap + x_shift
        z0 = derived.transformed_max_y - params.pad_thickness + params.pad_offset_y + z_shift
        x1 = x0 + params.pad_length + params.pad_overlap
        z1 = z0 + params.pad_thickness
        pad_profile_xz = [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
        parts.append(_revolve_closed_profile(pad_profile_xz, params.sweep_angle))

    if not parts:
        raise ValueError("Both c-clamp and pad are disabled; nothing to build.")

    merged = parts[0]
    for piece in parts[1:]:
        merged = merged + piece
    return merged.rotate(Axis.X, 90.0)


def print_checks(params: CClampParams, derived: Derived, model) -> None:
    print(f"INFO: sweep_angle_deg = {params.sweep_angle:.3f}")
    print(f"INFO: radius_ref_mode = {params.radius_ref_mode}")
    print(f"INFO: profile_scale_x = {derived.scale_x:.4f}")
    print(f"INFO: base_back_wall_height_mm = {derived.base_back_wall_height:.3f}")
    print(f"INFO: base_back_wall_mid_y_mm = {derived.base_back_wall_mid_y:.3f}")
    print(f"INFO: target_back_wall_height_mm = {params.back_wall_height_target:.3f}")
    print(f"INFO: back_wall_delta_mm = {derived.back_wall_delta:.3f}")
    print(f"INFO: transformed_profile_width_mm = {derived.transformed_max_x - derived.transformed_min_x:.3f}")
    print(f"INFO: transformed_profile_height_mm = {derived.transformed_max_y - derived.transformed_min_y:.3f}")
    print(f"INFO: mount_outer_radius_mm = {derived.mount_outer_radius:.3f}")
    print(f"INFO: pad_outer_radius_mm = {derived.pad_outer_radius:.3f}")
    print(f"INFO: sweep_chord_estimate_mm = {derived.sweep_chord_estimate:.3f}")
    print(f"INFO: sweep_arc_estimate_mm = {derived.sweep_arc_estimate:.3f}")
    print(f"INFO: attachment_support = {'enabled' if params.enable_attachment_support else 'disabled'}")

    if params.sweep_angle <= 0:
        print("WARNING: sweep_angle must be positive.")
    if params.sweep_angle > 180:
        print("WARNING: sweep_angle > 180 may be hard to print/install.")
    if params.radius <= 0:
        print("WARNING: radius must be positive.")
    if params.profile_width_target < params.min_profile_width_recommended:
        print("WARNING: profile_width_target is below recommended minimum.")
    if params.back_wall_height_target < params.min_back_wall_height_recommended:
        print("WARNING: back_wall_height_target is below recommended minimum.")
    if params.pad_length > params.max_projection:
        print("WARNING: pad_length exceeds max_projection.")

    bb = model.bounding_box()
    size = bb.size
    if size.X > params.ender3_v3_bed_x or size.Y > params.ender3_v3_bed_y:
        print("WARNING: XY footprint exceeds Ender 3 V3 bed (220x220 mm).")


def print_geometry_summary(model) -> None:
    bb = model.bounding_box()
    size = bb.size
    print(
        "SUMMARY: bbox_min=(%.2f, %.2f, %.2f) bbox_max=(%.2f, %.2f, %.2f) size=(%.2f, %.2f, %.2f) mm"
        % (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z, size.X, size.Y, size.Z)
    )
    print(f"SUMMARY: CAD volume estimate = {model.volume / 1000.0:.2f} ml")


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
    parser = argparse.ArgumentParser(description="Parameterized C-clamp sweep in build123d.")
    parser.add_argument(
        "--output",
        "-o",
        default=str(DEFAULT_OUTPUT),
        help=f"Output STL path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--profile-width",
        type=float,
        default=PRIMARY_PROFILE_WIDTH_MM,
        help="Target profile width in mm (default: canonical width)",
    )
    parser.add_argument(
        "--back-wall-height",
        type=float,
        default=PRIMARY_BACK_WALL_HEIGHT_MM,
        help="Target straight back-wall height in mm (default: canonical)",
    )
    parser.add_argument(
        "--mouth-relief",
        type=float,
        default=PRIMARY_MOUTH_RELIEF_MM,
        help="Additional opening-side widening near top in mm (default: 0.0)",
    )
    parser.add_argument(
        "--profile-radial-offset",
        type=float,
        default=PRIMARY_PROFILE_RADIAL_OFFSET_MM,
        help="Radial offset applied to the full profile in mm",
    )
    parser.add_argument(
        "--radius",
        type=float,
        default=PRIMARY_RADIUS_MM,
        help="Sweep radius in mm",
    )
    parser.add_argument(
        "--sweep-angle",
        type=float,
        default=PRIMARY_SWEEP_ANGLE_DEG,
        help="Sweep angle in degrees",
    )
    parser.add_argument(
        "--pad-length",
        type=float,
        default=PRIMARY_PAD_LENGTH_MM,
        help="Pad radial length in mm",
    )
    parser.add_argument(
        "--attachment-support",
        action=argparse.BooleanOptionalAction,
        default=PRIMARY_ATTACHMENT_SUPPORT_ENABLED,
        help="Enable attachment support stub (pad). Disable to keep back wall as outermost edge.",
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
        profile_width=args.profile_width,
        back_wall_height=args.back_wall_height,
        mouth_relief=args.mouth_relief,
        profile_radial_offset=args.profile_radial_offset,
        radius=args.radius,
        sweep_angle=args.sweep_angle,
        pad_length=args.pad_length,
        attachment_support=args.attachment_support,
    )


def runtime_from_head_config() -> RuntimeOptions:
    return RuntimeOptions(
        output=Path(HEAD_OUTPUT),
        preview=HEAD_PREVIEW,
        export=HEAD_EXPORT,
        profile_width=PRIMARY_PROFILE_WIDTH_MM,
        back_wall_height=PRIMARY_BACK_WALL_HEIGHT_MM,
        mouth_relief=PRIMARY_MOUTH_RELIEF_MM,
        profile_radial_offset=PRIMARY_PROFILE_RADIAL_OFFSET_MM,
        radius=PRIMARY_RADIUS_MM,
        sweep_angle=PRIMARY_SWEEP_ANGLE_DEG,
        pad_length=PRIMARY_PAD_LENGTH_MM,
        attachment_support=PRIMARY_ATTACHMENT_SUPPORT_ENABLED,
    )


def main() -> int:
    run = runtime_from_head_config() if USE_HEAD_CONFIG else runtime_from_args(parse_args())
    params = CClampParams(
        profile_width_target=run.profile_width,
        back_wall_height_target=run.back_wall_height,
        mouth_relief=run.mouth_relief,
        profile_radial_offset=run.profile_radial_offset,
        radius=run.radius,
        sweep_angle=run.sweep_angle,
        pad_length=run.pad_length,
        enable_attachment_support=run.attachment_support,
    )
    profile = load_c_clamp_profile()
    derived = derive(params, profile)

    model = build_c_clamp_sweep(params, derived)
    print_checks(params, derived, model)
    print_geometry_summary(model)

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
