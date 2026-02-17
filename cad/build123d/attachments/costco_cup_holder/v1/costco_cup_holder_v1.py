#!/usr/bin/env python3
"""build123d port of attachments/costco_cup_holder/v1/costco_cup_holder_v1.scad."""

from __future__ import annotations

import argparse
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from build123d import (
        Align,
        Axis,
        Box,
        BuildLine,
        BuildPart,
        BuildSketch,
        Cylinder,
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


# -------------------------------
# Primary knobs (edit these first)
# -------------------------------
PRIMARY_SWEEP_ANGLE_DEG = 24.0
PRIMARY_RADIUS_MM = 222.25
PRIMARY_PAD_LENGTH_MM = 0.0
PRIMARY_CUP_LIP_DIAMETER_MM = 97.0
PRIMARY_CUP_BODY_DIAMETER_BELOW_LIP_MM = 93.5
PRIMARY_RING_THICKNESS_MM = 5.5
PRIMARY_CLEARANCE_MM = 0.35
PRIMARY_HOLDER_TILT_DEG = 0.0
PRIMARY_HOLDER_RADIAL_LOCATION_ON_PAD_MM = 0.0
PRIMARY_HOOP_CENTER_OFFSET_FROM_MOUNT_MM = (
    PRIMARY_CUP_BODY_DIAMETER_BELOW_LIP_MM + 2.0 * PRIMARY_CLEARANCE_MM + 2.0 * PRIMARY_RING_THICKNESS_MM
) * 0.5
PRIMARY_SWEEP_FIT_MODE = "auto_hoop_kiss"  # "manual" or "auto_hoop_kiss"
PRIMARY_SWEEP_FIT_DIAMETER_MODE = "hoop_outer"  # "hoop_outer" or "cup_lip_exterior"


REPO_ROOT = Path(__file__).resolve().parents[5]
CORE_PROFILE_SCAD = REPO_ROOT / "core_mount_system/c_clamp/v1/c_clamp_profile_topref_v1.scad"
DEFAULT_OUTPUT = REPO_ROOT / "build/costco_cup_holder_v1_b123d.stl"
DEFAULT_HOLDER_ONLY_OUTPUT = REPO_ROOT / "build/costco_cup_holder_v1_b123d_holder_only.stl"

# -------------------------------
# Run config (same names across scripts)
# -------------------------------
USE_HEAD_CONFIG = True
HEAD_PREVIEW = False
HEAD_EXPORT = True
HEAD_OUTPUT = DEFAULT_OUTPUT
HEAD_HOLDER_ONLY = False


@dataclass(frozen=True)
class RuntimeOptions:
    output: Path
    holder_only: bool
    preview: bool
    export: bool
    cup_lip_diameter: float
    cup_body_diameter_below_lip: float
    ring_thickness: float
    clearance: float
    holder_tilt_deg: float
    holder_radial_location_on_pad: float
    hoop_center_offset_from_mount: float
    sweep_fit_mode: str
    sweep_fit_diameter_mode: str


@dataclass(frozen=True)
class CClampProfile:
    min_profile_x: float
    max_profile_x: float
    min_profile_y: float
    max_profile_y: float
    hook_center_x: float
    points: list[tuple[float, float]]


@dataclass(frozen=True)
class CostcoCupHolderParams:
    # -------------------------------
    # Quick Tuning
    # -------------------------------
    show_clamp: bool = True
    show_pad: bool = False
    show_holder: bool = True

    sweep_angle: float = PRIMARY_SWEEP_ANGLE_DEG
    sweep_fit_mode: str = PRIMARY_SWEEP_FIT_MODE
    sweep_fit_diameter_mode: str = PRIMARY_SWEEP_FIT_DIAMETER_MODE
    sweep_kiss_clearance: float = 0.0

    radius: float = PRIMARY_RADIUS_MM
    radius_ref_mode: str = "hook_center"  # "hook_center" or "outer_edge"
    axis_z: float = 0.0

    pad_length: float = PRIMARY_PAD_LENGTH_MM
    pad_thickness: float = 5.0
    pad_overlap: float = 1.0
    pad_offset_y: float = 0.0  # preserve max_profile_y top-reference intent

    cup_lip_diameter: float = PRIMARY_CUP_LIP_DIAMETER_MM
    cup_body_diameter_below_lip: float = PRIMARY_CUP_BODY_DIAMETER_BELOW_LIP_MM
    ring_thickness: float = PRIMARY_RING_THICKNESS_MM
    clearance: float = PRIMARY_CLEARANCE_MM
    ring_height: float = 14.0

    attach_angle: float = PRIMARY_SWEEP_ANGLE_DEG * 0.5
    attach_angle_mode: str = "auto_center"  # "auto_center" or "manual"
    holder_radial_location_on_pad: float = PRIMARY_HOLDER_RADIAL_LOCATION_ON_PAD_MM
    holder_top_offset: float = 0.0
    holder_tilt_deg: float = PRIMARY_HOLDER_TILT_DEG

    hoop_center_offset_from_mount: float = PRIMARY_HOOP_CENTER_OFFSET_FROM_MOUNT_MM
    bridge_width: float = 42.0
    bridge_thickness: float = 14.0
    bridge_overlap_into_ring: float = PRIMARY_RING_THICKNESS_MM
    bridge_overlap_into_clamp: float = 2.0

    # -------------------------------
    # Strength / Printability
    # -------------------------------
    enable_mount_gusset: bool = False
    mount_gusset_width: float = 30.0
    mount_gusset_mount_inset: float = 3.0
    mount_gusset_ring_inset: float = 1.0
    mount_gusset_base_depth: float = 14.0
    mount_gusset_base_height: float = 5.0
    mount_gusset_top_depth: float = 3.0
    mount_gusset_top_height: float = 12.0

    # -------------------------------
    # Advanced Controls
    # -------------------------------
    under_hoop_open_margin: float = 2.0


@dataclass(frozen=True)
class Derived:
    radius_ref_x: float
    axis_x: float
    axis_shift_x: float
    attach_x: float
    attach_profile_y_2d: float
    attach_profile_y_sweep: float
    attach_r: float
    hoop_inner_diameter: float
    hoop_outer_diameter: float
    hoop_outer_radius: float
    lip_seat_radial_margin: float
    hoop_center_radial_for_sweep: float
    sweep_fit_radius: float
    sweep_half_angle_auto: float
    sweep_angle_auto: float
    sweep_angle_effective: float
    attach_angle_effective: float
    bridge_length: float
    pad_outer_x_from_mount: float
    hole_min_x_from_mount: float


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


def derive(params: CostcoCupHolderParams, profile: CClampProfile) -> Derived:
    radius_ref_x = profile.hook_center_x if params.radius_ref_mode == "hook_center" else profile.max_profile_x
    axis_x = radius_ref_x - params.radius
    axis_shift_x = max(0.0, axis_x - profile.min_profile_x + 0.1)

    attach_x = profile.max_profile_x + params.holder_radial_location_on_pad
    attach_profile_y_2d = profile.max_profile_y + params.holder_top_offset
    attach_profile_y_sweep = attach_profile_y_2d - params.axis_z
    attach_r = axis_shift_x + (attach_x - axis_x)

    hoop_inner_diameter = params.cup_body_diameter_below_lip + (2.0 * params.clearance)
    hoop_outer_diameter = hoop_inner_diameter + (2.0 * params.ring_thickness)
    hoop_outer_radius = hoop_outer_diameter * 0.5
    lip_seat_radial_margin = (params.cup_lip_diameter - hoop_inner_diameter) * 0.5

    hoop_center_radial_for_sweep = attach_r + (params.hoop_center_offset_from_mount * math.cos(math.radians(params.holder_tilt_deg)))
    fit_diameter = params.cup_lip_diameter if params.sweep_fit_diameter_mode == "cup_lip_exterior" else hoop_outer_diameter
    sweep_fit_radius = (fit_diameter * 0.5) + params.sweep_kiss_clearance
    if hoop_center_radial_for_sweep > 0:
        ratio = max(-1.0, min(1.0, sweep_fit_radius / hoop_center_radial_for_sweep))
        sweep_half_angle_auto = math.degrees(math.asin(ratio))
    else:
        sweep_half_angle_auto = 90.0
    sweep_angle_auto = 2.0 * sweep_half_angle_auto

    sweep_angle_effective = sweep_angle_auto if params.sweep_fit_mode == "auto_hoop_kiss" else params.sweep_angle
    attach_angle_effective = sweep_angle_effective * 0.5 if params.attach_angle_mode == "auto_center" else params.attach_angle

    bridge_length = max(0.1, params.hoop_center_offset_from_mount - hoop_outer_radius + params.bridge_overlap_into_ring)

    pad_outer_x_from_mount = params.pad_length - params.holder_radial_location_on_pad
    hole_min_x_from_mount = params.hoop_center_offset_from_mount - (hoop_inner_diameter * 0.5)

    return Derived(
        radius_ref_x=radius_ref_x,
        axis_x=axis_x,
        axis_shift_x=axis_shift_x,
        attach_x=attach_x,
        attach_profile_y_2d=attach_profile_y_2d,
        attach_profile_y_sweep=attach_profile_y_sweep,
        attach_r=attach_r,
        hoop_inner_diameter=hoop_inner_diameter,
        hoop_outer_diameter=hoop_outer_diameter,
        hoop_outer_radius=hoop_outer_radius,
        lip_seat_radial_margin=lip_seat_radial_margin,
        hoop_center_radial_for_sweep=hoop_center_radial_for_sweep,
        sweep_fit_radius=sweep_fit_radius,
        sweep_half_angle_auto=sweep_half_angle_auto,
        sweep_angle_auto=sweep_angle_auto,
        sweep_angle_effective=sweep_angle_effective,
        attach_angle_effective=attach_angle_effective,
        bridge_length=bridge_length,
        pad_outer_x_from_mount=pad_outer_x_from_mount,
        hole_min_x_from_mount=hole_min_x_from_mount,
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


def build_clamp_pad_sweep(params: CostcoCupHolderParams, profile: CClampProfile, derived: Derived):
    parts = []
    x_shift = derived.axis_shift_x - derived.axis_x
    z_shift = -params.axis_z

    if params.show_clamp:
        clamp_profile_xz = [(x + x_shift, y + z_shift) for (x, y) in profile.points]
        parts.append(_revolve_closed_profile(clamp_profile_xz, derived.sweep_angle_effective))

    if params.show_pad and params.pad_length > 0:
        x0 = profile.max_profile_x - params.pad_overlap + x_shift
        z0 = profile.max_profile_y - params.pad_thickness + params.pad_offset_y + z_shift
        x1 = x0 + params.pad_length + params.pad_overlap
        z1 = z0 + params.pad_thickness
        pad_profile_xz = [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
        parts.append(_revolve_closed_profile(pad_profile_xz, derived.sweep_angle_effective))

    if not parts:
        return None

    merged = parts[0]
    for piece in parts[1:]:
        merged = merged + piece
    return merged.rotate(Axis.X, 90.0)


def build_holder_linear(params: CostcoCupHolderParams, derived: Derived):
    # Ring top is flush to clamp top-reference plane (z=0 in holder-local frame).
    ring_z0 = -params.ring_height
    outer = Cylinder(
        radius=derived.hoop_outer_diameter * 0.5,
        height=params.ring_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).translate((0.0, 0.0, ring_z0))
    inner = Cylinder(
        radius=derived.hoop_inner_diameter * 0.5,
        height=params.ring_height + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).translate((0.0, 0.0, ring_z0 - 0.1))
    hoop = (outer - inner).translate((params.hoop_center_offset_from_mount, 0.0, 0.0))

    # Full-height near-side connector for a beefier clamp-to-ring load path.
    bridge_height_eff = max(params.ring_height, params.bridge_thickness)
    bridge = Box(
        derived.bridge_length + params.bridge_overlap_into_clamp,
        params.bridge_width,
        bridge_height_eff,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    ).translate((-params.bridge_overlap_into_clamp, 0.0, -bridge_height_eff))

    holder = bridge + hoop

    if params.enable_mount_gusset:
        gusset_width_eff = min(params.mount_gusset_width, params.bridge_width)
        x_base = max(0.0, params.mount_gusset_mount_inset)
        x_top = max(
            x_base + 0.1,
            params.hoop_center_offset_from_mount - derived.hoop_outer_radius + params.mount_gusset_ring_inset,
        )
        z_top = max(params.bridge_thickness, params.ring_height - params.mount_gusset_top_height)

        gusset_span_x = max(0.1, (x_top + params.mount_gusset_top_depth) - x_base)
        gusset_base = Box(
            gusset_span_x,
            gusset_width_eff,
            params.mount_gusset_base_height,
            align=(Align.MIN, Align.CENTER, Align.MIN),
        ).translate((x_base, 0.0, 0.0))
        gusset_top = Box(
            params.mount_gusset_top_depth,
            gusset_width_eff,
            params.mount_gusset_top_height,
            align=(Align.MIN, Align.CENTER, Align.MIN),
        ).translate((x_top, 0.0, z_top))
        gusset = gusset_base + gusset_top
        holder = holder + gusset

    return holder


def build_holder_positioned(holder_linear, params: CostcoCupHolderParams, derived: Derived):
    holder = holder_linear.rotate(Axis.Y, params.holder_tilt_deg)
    holder = holder.translate((derived.attach_r, 0.0, derived.attach_profile_y_sweep))
    holder = holder.rotate(Axis.Z, derived.attach_angle_effective)
    return holder.rotate(Axis.X, 90.0)


def build_assembly(params: CostcoCupHolderParams, profile: CClampProfile, holder_only: bool):
    derived = derive(params, profile)
    holder_linear = build_holder_linear(params, derived)

    if holder_only:
        return holder_linear, derived

    parts = []
    clamp_pad = build_clamp_pad_sweep(params, profile, derived)
    if clamp_pad is not None:
        parts.append(clamp_pad)

    if params.show_holder:
        parts.append(build_holder_positioned(holder_linear, params, derived))

    if not parts:
        raise ValueError("Nothing enabled to build.")

    merged = parts[0]
    for piece in parts[1:]:
        merged = merged + piece
    return merged, derived


def print_checks(params: CostcoCupHolderParams, derived: Derived, model, holder_only: bool) -> None:
    mode = "holder-only" if holder_only else "full"
    print(f"INFO: mode = {mode}")
    print(f"INFO: sweep_fit_mode = {params.sweep_fit_mode}")
    print(f"INFO: sweep_fit_diameter_mode = {params.sweep_fit_diameter_mode}")
    print(f"INFO: sweep_angle_effective_deg = {derived.sweep_angle_effective:.3f}")
    print(f"INFO: attach_angle_effective_deg = {derived.attach_angle_effective:.3f}")
    print(f"INFO: hoop_inner_diameter_mm = {derived.hoop_inner_diameter:.3f}")
    print(f"INFO: hoop_outer_diameter_mm = {derived.hoop_outer_diameter:.3f}")
    ring_near_side_x = params.hoop_center_offset_from_mount - derived.hoop_outer_radius
    print(f"INFO: ring_to_clamp_touch_gap_mm = {ring_near_side_x:.3f}")
    print(f"INFO: bridge_length_mm = {derived.bridge_length:.3f}")
    print(f"INFO: bridge_height_mm = {max(params.ring_height, params.bridge_thickness):.3f}")
    print(f"INFO: bridge_overlap_into_clamp_mm = {params.bridge_overlap_into_clamp:.3f}")
    print(f"INFO: lip_seat_radial_margin_mm = {derived.lip_seat_radial_margin:.3f}")
    if params.show_pad and params.pad_length > 0:
        print(f"INFO: under_hoop_open_gap_mm = {derived.hole_min_x_from_mount - derived.pad_outer_x_from_mount:.3f}")
    else:
        print("INFO: under_hoop_open_gap_mm = N/A (pad disabled)")

    if params.show_pad and (params.holder_radial_location_on_pad < 0 or params.holder_radial_location_on_pad > params.pad_length):
        print("WARNING: holder_radial_location_on_pad is outside pad_length.")
    if derived.lip_seat_radial_margin <= 0:
        print("WARNING: cup lip will not seat. Increase cup_lip_diameter or reduce hole diameter.")
    if params.ring_thickness < 3:
        print("WARNING: ring_thickness < 3 mm may be weak for loaded cup.")
    if derived.bridge_length <= 0.5:
        print("WARNING: hoop center is too close to mount; bridge has near-zero length.")
    if params.bridge_overlap_into_clamp <= 0:
        print("WARNING: bridge_overlap_into_clamp <= 0; connector may only touch clamp tangentially.")
    if abs(ring_near_side_x) > 0.2:
        print("WARNING: ring near side is not flush with clamp bond plane; adjust hoop_center_offset_from_mount.")
    if params.bridge_overlap_into_ring > params.ring_thickness:
        print("WARNING: bridge_overlap_into_ring exceeds ring_thickness; may intrude into cup path.")
    if params.enable_mount_gusset and params.mount_gusset_ring_inset + params.mount_gusset_top_depth > params.ring_thickness:
        print("WARNING: gusset tip may intrude into cup path; reduce ring_inset and/or top_depth.")
    if params.show_pad and params.pad_length > 0 and derived.hole_min_x_from_mount <= derived.pad_outer_x_from_mount + params.under_hoop_open_margin:
        print("WARNING: hole overlaps pad under the hoop. Increase hoop_center_offset_from_mount and/or holder_radial_location_on_pad.")
    if params.sweep_fit_mode == "auto_hoop_kiss" and derived.hoop_center_radial_for_sweep <= derived.sweep_fit_radius:
        print("WARNING: auto sweep-fit invalid; sweep-fit radius exceeds hoop center radius.")

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
    parser = argparse.ArgumentParser(description="build123d Costco cup holder v1 (ported from SCAD).")
    parser.add_argument(
        "--output",
        "-o",
        default=str(DEFAULT_OUTPUT),
        help=f"Output STL path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--holder-only",
        action="store_true",
        help="Build/export holder-only sample (no clamp/pad sweep).",
    )
    parser.add_argument(
        "--cup-lip-diameter",
        type=float,
        default=PRIMARY_CUP_LIP_DIAMETER_MM,
        help="Cup lip outer diameter (mm).",
    )
    parser.add_argument(
        "--cup-body-diameter-below-lip",
        type=float,
        default=PRIMARY_CUP_BODY_DIAMETER_BELOW_LIP_MM,
        help="Cup body outer diameter below lip (mm).",
    )
    parser.add_argument(
        "--ring-thickness",
        type=float,
        default=PRIMARY_RING_THICKNESS_MM,
        help="Hoop wall thickness (mm).",
    )
    parser.add_argument(
        "--clearance",
        type=float,
        default=PRIMARY_CLEARANCE_MM,
        help="Clearance added to cup body diameter (mm).",
    )
    parser.add_argument(
        "--holder-tilt-deg",
        type=float,
        default=PRIMARY_HOLDER_TILT_DEG,
        help="Holder tilt in degrees.",
    )
    parser.add_argument(
        "--holder-radial-location-on-pad",
        type=float,
        default=PRIMARY_HOLDER_RADIAL_LOCATION_ON_PAD_MM,
        help="Holder radial location on pad (mm).",
    )
    parser.add_argument(
        "--hoop-center-offset-from-mount",
        type=float,
        default=PRIMARY_HOOP_CENTER_OFFSET_FROM_MOUNT_MM,
        help="Radial offset from mount origin to hoop center (mm).",
    )
    parser.add_argument(
        "--sweep-fit-mode",
        choices=("manual", "auto_hoop_kiss"),
        default=PRIMARY_SWEEP_FIT_MODE,
        help="Sweep angle mode.",
    )
    parser.add_argument(
        "--sweep-fit-diameter-mode",
        choices=("hoop_outer", "cup_lip_exterior"),
        default=PRIMARY_SWEEP_FIT_DIAMETER_MODE,
        help="Diameter used for auto sweep-fit.",
    )
    default_preview = len(sys.argv) == 1
    parser.add_argument(
        "--preview",
        action="store_true",
        default=default_preview,
        help="Show preview in OCP CAD Viewer and skip STL export unless --export is also set.",
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="When used with --preview, also export STL.",
    )
    return parser.parse_args()


def runtime_from_args(args: argparse.Namespace) -> RuntimeOptions:
    out_path = Path(args.output)
    if args.holder_only and out_path == DEFAULT_OUTPUT:
        out_path = DEFAULT_HOLDER_ONLY_OUTPUT
    return RuntimeOptions(
        output=out_path,
        holder_only=args.holder_only,
        preview=args.preview,
        export=args.export,
        cup_lip_diameter=args.cup_lip_diameter,
        cup_body_diameter_below_lip=args.cup_body_diameter_below_lip,
        ring_thickness=args.ring_thickness,
        clearance=args.clearance,
        holder_tilt_deg=args.holder_tilt_deg,
        holder_radial_location_on_pad=args.holder_radial_location_on_pad,
        hoop_center_offset_from_mount=args.hoop_center_offset_from_mount,
        sweep_fit_mode=args.sweep_fit_mode,
        sweep_fit_diameter_mode=args.sweep_fit_diameter_mode,
    )


def runtime_from_head_config() -> RuntimeOptions:
    output = DEFAULT_HOLDER_ONLY_OUTPUT if HEAD_HOLDER_ONLY else Path(HEAD_OUTPUT)
    return RuntimeOptions(
        output=output,
        holder_only=HEAD_HOLDER_ONLY,
        preview=HEAD_PREVIEW,
        export=HEAD_EXPORT,
        cup_lip_diameter=PRIMARY_CUP_LIP_DIAMETER_MM,
        cup_body_diameter_below_lip=PRIMARY_CUP_BODY_DIAMETER_BELOW_LIP_MM,
        ring_thickness=PRIMARY_RING_THICKNESS_MM,
        clearance=PRIMARY_CLEARANCE_MM,
        holder_tilt_deg=PRIMARY_HOLDER_TILT_DEG,
        holder_radial_location_on_pad=PRIMARY_HOLDER_RADIAL_LOCATION_ON_PAD_MM,
        hoop_center_offset_from_mount=PRIMARY_HOOP_CENTER_OFFSET_FROM_MOUNT_MM,
        sweep_fit_mode=PRIMARY_SWEEP_FIT_MODE,
        sweep_fit_diameter_mode=PRIMARY_SWEEP_FIT_DIAMETER_MODE,
    )


def main() -> int:
    run = runtime_from_head_config() if USE_HEAD_CONFIG else runtime_from_args(parse_args())
    params = CostcoCupHolderParams(
        cup_lip_diameter=run.cup_lip_diameter,
        cup_body_diameter_below_lip=run.cup_body_diameter_below_lip,
        ring_thickness=run.ring_thickness,
        clearance=run.clearance,
        holder_tilt_deg=run.holder_tilt_deg,
        holder_radial_location_on_pad=run.holder_radial_location_on_pad,
        hoop_center_offset_from_mount=run.hoop_center_offset_from_mount,
        sweep_fit_mode=run.sweep_fit_mode,
        sweep_fit_diameter_mode=run.sweep_fit_diameter_mode,
    )
    profile = load_c_clamp_profile()
    model, derived = build_assembly(params, profile, holder_only=run.holder_only)
    print_checks(params, derived, model, holder_only=run.holder_only)

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
