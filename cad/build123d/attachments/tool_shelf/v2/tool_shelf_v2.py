#!/usr/bin/env python3
"""build123d port of attachments/tool_shelf/v1/tool_shelf_v1.scad."""

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
PRIMARY_PAD_LENGTH_MM = 35.0
PRIMARY_ARC_LENGTH_MM = 152.4
PRIMARY_RADIAL_WIDTH_MM = 152.4
PRIMARY_FLOOR_THICKNESS_MM = 4.0
PRIMARY_HOLDER_TILT_DEG = 4.0
PRIMARY_HOLDER_RADIAL_LOCATION_ON_PAD_MM = 0.0
PRIMARY_INNER_OVERHANG_MM = 6.0
PRIMARY_CLAMP_BACK_WALL_STRETCH_MM = 0.0
PRIMARY_ATTACHMENT_SUPPORT_ENABLED = True

try:
    from build123d import (
        Align,
        Axis,
        Box,
        BuildLine,
        BuildPart,
        BuildSketch,
        Plane,
        Polyline,
        export_stl,
        extrude,
        loft,
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
DEFAULT_OUTPUT = REPO_ROOT / "build/tool_shelf_v2_b123d.stl"

# -------------------------------
# Run config (same names across scripts)
# -------------------------------
USE_HEAD_CONFIG = False
HEAD_PREVIEW = True
HEAD_EXPORT = False
HEAD_OUTPUT = DEFAULT_OUTPUT
HEAD_HOLDER_ONLY = False


@dataclass(frozen=True)
class RuntimeOptions:
    output: Path
    holder_only: bool
    clamp_back_wall_stretch: float
    attachment_support: bool
    preview: bool
    export: bool


@dataclass(frozen=True)
class CClampProfile:
    min_profile_x: float
    max_profile_x: float
    min_profile_y: float
    max_profile_y: float
    hook_center_x: float
    points: list[tuple[float, float]]


@dataclass(frozen=True)
class ToolShelfParams:
    # -------------------------------
    # Quick Tuning
    # -------------------------------
    render_holder_only: bool = False
    show_clamp: bool = True
    show_pad: bool = True
    enable_attachment_support: bool = PRIMARY_ATTACHMENT_SUPPORT_ENABLED
    show_shelf: bool = True
    show_lips: bool = True
    show_gusset: bool = True
    align_to_sweep_edges: bool = True

    sweep_angle: float = PRIMARY_SWEEP_ANGLE_DEG
    radius: float = PRIMARY_RADIUS_MM
    radius_ref_mode: str = "hook_center"
    axis_z: float = 0.0
    clamp_back_wall_stretch: float = PRIMARY_CLAMP_BACK_WALL_STRETCH_MM

    pad_length: float = PRIMARY_PAD_LENGTH_MM
    pad_thickness: float = 4.0
    pad_overlap: float = 1.0
    pad_offset_y: float = 0.0

    holder_top_offset: float = 0.0
    holder_tilt_deg: float = PRIMARY_HOLDER_TILT_DEG
    holder_angle_offset: float = 0.0
    holder_radial_location_on_pad: float = PRIMARY_HOLDER_RADIAL_LOCATION_ON_PAD_MM

    arc_length: float = PRIMARY_ARC_LENGTH_MM
    radial_width: float = PRIMARY_RADIAL_WIDTH_MM
    floor_thickness: float = PRIMARY_FLOOR_THICKNESS_MM
    lip_thickness: float = 3.0
    lip_height_near: float = 14.0
    lip_height_far: float = 6.0
    lip_height_sides: float = 12.0
    lip_height_side_end: float = 12.0
    side_wall_thickness: float = 3.0
    side_wall_drop: float = 10.0
    corner_radius: float = 8.0
    lip_corner_radius: float = 6.0
    corner_gap_size: float = 5.0
    inner_overhang: float = PRIMARY_INNER_OVERHANG_MM

    gusset_thickness: float = 6.0
    gusset_height: float = 25.0
    gusset_width: float = 45.0
    gusset_back_overhang: float = 4.0
    gusset_flare: float = 8.0
    gusset_max_overhang_deg: float = 45.0
    gusset_attach_overlap: float = 2.0
    gusset_top_flat: float = 2.0

    clamp_cap_thickness: float = 3.0
    clamp_cap_width: float = 18.0
    enable_clamp_channel: bool = False
    clamp_channel_width: float = 10.0
    clamp_channel_depth: float = 2.0
    clamp_channel_offset: float = 0.0

    max_projection: float = 127.0
    enable_drain_notch: bool = True
    drain_notch_width: float = 8.0

    # -------------------------------
    # Strength / Printability
    # -------------------------------
    min_floor_thickness_recommended: float = 2.0
    min_lip_thickness_recommended: float = 2.0
    min_gusset_thickness_recommended: float = 4.0
    min_gusset_height_recommended: float = 18.0
    mount_flat_wall_height_available: float = 45.4

    # -------------------------------
    # Advanced Controls
    # -------------------------------
    ender3_v3_bed_x: float = 220.0
    ender3_v3_bed_y: float = 220.0


@dataclass(frozen=True)
class Derived:
    radius_ref_x: float
    axis_x: float
    axis_shift_x: float
    mount_wall_radius: float
    pad_outer_radius: float
    holder_origin_x: float
    holder_profile_y_2d: float
    holder_profile_y_sweep: float
    inner_radius: float
    outer_radius: float
    centerline_radius: float
    arc_angle_deg: float
    shelf_angle_deg: float
    attach_angle: float
    a_start: float
    a_end: float
    shelf_start_angle: float
    shelf_end_angle: float
    projection_from_pad_outer: float
    side_wall_angle_deg: float
    gap_angle_deg: float
    corner_radius_eff: float
    lip_corner_radius_eff: float
    arc_length_effective: float
    lip_height_max: float
    gusset_top_flat_eff: float
    gusset_depth: float
    gusset_base_min: float
    gusset_base_span: float
    gusset_r0: float
    gusset_r1: float
    gusset_span_angle: float
    gusset_a0: float
    gusset_a1: float
    mask_r_in: float
    mask_r_out: float
    mask_z0: float
    mask_height: float
    footprint_x: float
    footprint_y: float


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
    tol = 1e-5
    wall_ys = [y for (x, y) in profile.points if abs(x - profile.max_profile_x) <= tol]
    if not wall_ys:
        raise ValueError("Could not find canonical back-wall points at max_profile_x.")
    return min(wall_ys)


def stretch_profile_from_back_wall_mid(profile: CClampProfile, stretch_mm: float) -> CClampProfile:
    if abs(stretch_mm) <= 1e-9:
        return profile

    base_back_wall_bottom_y = _canonical_back_wall_bottom_y(profile)
    base_back_wall_mid_y = (profile.max_profile_y + base_back_wall_bottom_y) * 0.5
    upper_shift = stretch_mm * 0.5
    lower_shift = -stretch_mm * 0.5

    stretched_points = [
        (x, y + (upper_shift if y >= base_back_wall_mid_y else lower_shift))
        for (x, y) in profile.points
    ]
    ys = [y for (_, y) in stretched_points]
    return CClampProfile(
        min_profile_x=profile.min_profile_x,
        max_profile_x=profile.max_profile_x,
        min_profile_y=min(ys),
        max_profile_y=max(ys),
        hook_center_x=profile.hook_center_x,
        points=stretched_points,
    )


def _seg_count_for_span(a0_deg: float, a1_deg: float) -> int:
    return max(12, int(math.ceil(abs(a1_deg - a0_deg) / 3.0)))


def _arc_point(r: float, a_deg: float, cx: float) -> tuple[float, float]:
    a = math.radians(a_deg)
    return (cx + r * math.cos(a), r * math.sin(a))


def _arc_points(r: float, a0_deg: float, a1_deg: float, n: int, cx: float) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for i in range(n + 1):
        t = i / n
        points.append(_arc_point(r, a0_deg + (a1_deg - a0_deg) * t, cx))
    return points


def _annular_sector_points(r_in: float, r_out: float, a0_deg: float, a1_deg: float, cx: float) -> list[tuple[float, float]]:
    n = _seg_count_for_span(a0_deg, a1_deg)
    return _arc_points(r_out, a0_deg, a1_deg, n, cx) + _arc_points(r_in, a1_deg, a0_deg, n, cx)


def derive(params: ToolShelfParams, profile: CClampProfile) -> Derived:
    radius_ref_x = profile.hook_center_x if params.radius_ref_mode == "hook_center" else profile.max_profile_x
    axis_x = radius_ref_x - params.radius
    axis_shift_x = max(0.0, axis_x - profile.min_profile_x + 0.1)

    mount_wall_radius = axis_shift_x + (profile.max_profile_x - axis_x)
    pad_outer_radius = mount_wall_radius + params.pad_length

    holder_origin_x = profile.max_profile_x + params.holder_radial_location_on_pad
    holder_profile_y_2d = profile.max_profile_y + params.holder_top_offset
    holder_profile_y_sweep = holder_profile_y_2d - params.axis_z

    inner_radius = mount_wall_radius + params.holder_radial_location_on_pad - params.inner_overhang
    outer_radius = inner_radius + params.radial_width
    centerline_radius = (inner_radius + outer_radius) / 2.0

    arc_angle_deg = (params.arc_length / centerline_radius) * 180.0 / math.pi if centerline_radius > 0 else 0.0
    shelf_angle_deg = params.sweep_angle if params.align_to_sweep_edges else arc_angle_deg
    attach_angle = params.sweep_angle / 2.0 + params.holder_angle_offset

    a_start = -shelf_angle_deg / 2.0
    a_end = shelf_angle_deg / 2.0
    shelf_start_angle = attach_angle + a_start
    shelf_end_angle = attach_angle + a_end

    projection_from_pad_outer = outer_radius - pad_outer_radius
    side_wall_angle_deg = (
        max(0.4, (params.side_wall_thickness / centerline_radius) * 180.0 / math.pi) if centerline_radius > 0 else 0.4
    )
    gap_angle_deg = (params.corner_gap_size / inner_radius) * 180.0 / math.pi if inner_radius > 0 else 0.0

    corner_radius_eff = (
        min(params.corner_radius, max(0.0, params.radial_width / 2.0 - 0.2)) if params.corner_radius > 0 else 0.0
    )
    lip_corner_radius_eff = (
        min(params.lip_corner_radius, max(0.0, params.lip_thickness / 2.0 - 0.1))
        if params.lip_corner_radius > 0
        else 0.0
    )
    arc_length_effective = (shelf_angle_deg * math.pi / 180.0) * centerline_radius if centerline_radius > 0 else 0.0

    lip_height_max = max(
        params.lip_height_near,
        params.lip_height_far,
        params.lip_height_sides,
        params.lip_height_side_end,
    )

    gusset_top_flat_eff = max(params.gusset_top_flat, params.gusset_thickness)
    gusset_depth = max(0.0, max(params.gusset_thickness, params.inner_overhang + params.gusset_back_overhang))
    gusset_base_min = (
        gusset_top_flat_eff + (params.gusset_height / math.tan(math.radians(params.gusset_max_overhang_deg)))
        if params.gusset_max_overhang_deg > 0
        else 0.0
    )
    gusset_base_span = max(gusset_depth + params.gusset_flare, gusset_base_min)

    gusset_r0 = max(0.1, mount_wall_radius - params.gusset_attach_overlap)
    gusset_r1 = min(outer_radius, gusset_r0 + gusset_base_span)
    gusset_span_angle = (params.gusset_width / mount_wall_radius) * 180.0 / math.pi if mount_wall_radius > 0 else 0.0
    gusset_a0 = max(a_start, -gusset_span_angle / 2.0)
    gusset_a1 = min(a_end, gusset_span_angle / 2.0)

    mask_r_in = min(inner_radius, gusset_r0 - 0.4)
    mask_r_out = outer_radius + params.lip_thickness + 0.5
    mask_z0 = -params.floor_thickness - params.side_wall_drop - params.gusset_height - 1.0
    mask_height = (
        lip_height_max
        + params.clamp_cap_thickness
        + params.floor_thickness
        + params.side_wall_drop
        + params.gusset_height
        + 2.0
    )

    foot_n = _seg_count_for_span(shelf_start_angle, shelf_end_angle)
    foot_points = (
        _arc_points(outer_radius, shelf_start_angle, shelf_end_angle, foot_n, -mount_wall_radius)
        + _arc_points(inner_radius, shelf_end_angle, shelf_start_angle, foot_n, -mount_wall_radius)
        if shelf_angle_deg > 0 and outer_radius > inner_radius
        else []
    )
    if foot_points:
        xs = [p[0] for p in foot_points]
        ys = [p[1] for p in foot_points]
        footprint_x = max(xs) - min(xs)
        footprint_y = max(ys) - min(ys)
    else:
        footprint_x = 0.0
        footprint_y = 0.0

    return Derived(
        radius_ref_x=radius_ref_x,
        axis_x=axis_x,
        axis_shift_x=axis_shift_x,
        mount_wall_radius=mount_wall_radius,
        pad_outer_radius=pad_outer_radius,
        holder_origin_x=holder_origin_x,
        holder_profile_y_2d=holder_profile_y_2d,
        holder_profile_y_sweep=holder_profile_y_sweep,
        inner_radius=inner_radius,
        outer_radius=outer_radius,
        centerline_radius=centerline_radius,
        arc_angle_deg=arc_angle_deg,
        shelf_angle_deg=shelf_angle_deg,
        attach_angle=attach_angle,
        a_start=a_start,
        a_end=a_end,
        shelf_start_angle=shelf_start_angle,
        shelf_end_angle=shelf_end_angle,
        projection_from_pad_outer=projection_from_pad_outer,
        side_wall_angle_deg=side_wall_angle_deg,
        gap_angle_deg=gap_angle_deg,
        corner_radius_eff=corner_radius_eff,
        lip_corner_radius_eff=lip_corner_radius_eff,
        arc_length_effective=arc_length_effective,
        lip_height_max=lip_height_max,
        gusset_top_flat_eff=gusset_top_flat_eff,
        gusset_depth=gusset_depth,
        gusset_base_min=gusset_base_min,
        gusset_base_span=gusset_base_span,
        gusset_r0=gusset_r0,
        gusset_r1=gusset_r1,
        gusset_span_angle=gusset_span_angle,
        gusset_a0=gusset_a0,
        gusset_a1=gusset_a1,
        mask_r_in=mask_r_in,
        mask_r_out=mask_r_out,
        mask_z0=mask_z0,
        mask_height=mask_height,
        footprint_x=footprint_x,
        footprint_y=footprint_y,
    )


def _safe_fillet(part, edges: list, radius: float, label: str):
    if radius <= 0 or not edges:
        return part
    for scale in (1.0, 0.8, 0.6, 0.45, 0.3):
        try_radius = radius * scale
        if try_radius < 0.15:
            continue
        try:
            if scale < 0.999:
                print(f"INFO: {label} fillet reduced from {radius:.2f} to {try_radius:.2f}")
            return part.fillet(try_radius, edges)
        except Exception:
            continue
    print(f"WARN: skipped {label} fillet (r={radius:.2f})")
    return part


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


def _build_annular_sector_prism(
    r_in: float,
    r_out: float,
    a0_deg: float,
    a1_deg: float,
    z0: float,
    height: float,
    axis_r: float,
    fillet_r: float = 0.0,
    fillet_label: str = "sector",
):
    if r_out <= r_in or height <= 0 or a1_deg <= a0_deg:
        return None

    points = _annular_sector_points(r_in, r_out, a0_deg, a1_deg, -axis_r)
    with BuildPart() as part:
        with BuildSketch(Plane.XY.offset(z0)):
            with BuildLine():
                Polyline(*points, close=True)
            make_face()
        extrude(amount=height)

    solid = part.part
    if fillet_r > 0:
        solid = _safe_fillet(solid, list(solid.edges().filter_by(Axis.Z)), fillet_r, fillet_label)
    return solid


def _wall_band(
    params: ToolShelfParams,
    derived: Derived,
    r_in: float,
    r_out: float,
    h: float,
    a0: float,
    a1: float,
    z0: float,
    fillet: float,
    label: str,
):
    return _build_annular_sector_prism(
        r_in,
        r_out,
        a0,
        a1,
        z0=z0,
        height=h,
        axis_r=derived.mount_wall_radius,
        fillet_r=fillet,
        fillet_label=label,
    )


def build_clamp_pad_sweep(params: ToolShelfParams, profile: CClampProfile, derived: Derived):
    parts = []
    x_shift = derived.axis_shift_x - derived.axis_x
    z_shift = -params.axis_z

    if params.show_clamp:
        clamp_profile_xz = [(x + x_shift, y + z_shift) for (x, y) in profile.points]
        parts.append(_revolve_closed_profile(clamp_profile_xz, params.sweep_angle))

    if params.show_pad and params.enable_attachment_support and params.pad_length > 0:
        x0 = profile.max_profile_x - params.pad_overlap + x_shift
        z0 = profile.max_profile_y - params.pad_thickness + params.pad_offset_y + z_shift
        x1 = x0 + params.pad_length + params.pad_overlap
        z1 = z0 + params.pad_thickness
        pad_profile_xz = [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
        parts.append(_revolve_closed_profile(pad_profile_xz, params.sweep_angle))

    if not parts:
        return None

    merged = parts[0]
    for piece in parts[1:]:
        merged = merged + piece
    return merged.rotate(Axis.X, 90.0)


def _build_shelf_floor_linear(params: ToolShelfParams, derived: Derived):
    return _build_annular_sector_prism(
        derived.inner_radius,
        derived.outer_radius,
        derived.a_start,
        derived.a_end,
        z0=-params.floor_thickness,
        height=params.floor_thickness,
        axis_r=derived.mount_wall_radius,
        fillet_r=derived.corner_radius_eff,
        fillet_label="floor_corner",
    )


def _build_shelf_lips_linear(params: ToolShelfParams, derived: Derived) -> list:
    parts = []
    inner_a0 = derived.a_start + derived.gap_angle_deg
    inner_a1 = derived.a_end - derived.gap_angle_deg
    side_start_a1 = min(derived.a_end, derived.a_start + derived.side_wall_angle_deg)
    side_end_a0 = max(derived.a_start, derived.a_end - derived.side_wall_angle_deg)
    z_drop = -params.floor_thickness - params.side_wall_drop

    candidates = [
        _wall_band(
            params,
            derived,
            derived.inner_radius,
            derived.inner_radius + params.lip_thickness,
            params.lip_height_far,
            inner_a0,
            inner_a1,
            z0=0.0,
            fillet=derived.lip_corner_radius_eff,
            label="inner_lip",
        ),
        _wall_band(
            params,
            derived,
            derived.outer_radius - params.lip_thickness,
            derived.outer_radius,
            params.lip_height_near,
            derived.a_start,
            derived.a_end,
            z0=0.0,
            fillet=derived.lip_corner_radius_eff,
            label="outer_lip",
        ),
        _wall_band(
            params,
            derived,
            derived.inner_radius,
            derived.outer_radius,
            params.lip_height_sides,
            derived.a_start,
            side_start_a1,
            z0=0.0,
            fillet=derived.lip_corner_radius_eff,
            label="side_lip_start",
        ),
        _wall_band(
            params,
            derived,
            derived.inner_radius,
            derived.outer_radius,
            params.lip_height_side_end,
            side_end_a0,
            derived.a_end,
            z0=0.0,
            fillet=derived.lip_corner_radius_eff,
            label="side_lip_end",
        ),
        _wall_band(
            params,
            derived,
            derived.inner_radius,
            derived.outer_radius,
            params.side_wall_drop,
            derived.a_start,
            side_start_a1,
            z0=z_drop,
            fillet=derived.lip_corner_radius_eff,
            label="side_drop_start",
        ),
        _wall_band(
            params,
            derived,
            derived.inner_radius,
            derived.outer_radius,
            params.side_wall_drop,
            side_end_a0,
            derived.a_end,
            z0=z_drop,
            fillet=derived.lip_corner_radius_eff,
            label="side_drop_end",
        ),
        _wall_band(
            params,
            derived,
            derived.inner_radius,
            derived.inner_radius + params.lip_thickness,
            params.side_wall_drop,
            inner_a0,
            inner_a1,
            z0=z_drop,
            fillet=derived.lip_corner_radius_eff,
            label="inner_drop",
        ),
    ]

    for part in candidates:
        if part is not None:
            parts.append(part)
    return parts


def _build_shelf_clamp_cap_linear(params: ToolShelfParams, derived: Derived):
    cap_r1 = min(derived.outer_radius, derived.inner_radius + params.clamp_cap_width)
    return _wall_band(
        params,
        derived,
        derived.inner_radius,
        cap_r1,
        params.clamp_cap_thickness,
        derived.a_start,
        derived.a_end,
        z0=0.0,
        fillet=derived.lip_corner_radius_eff,
        label="clamp_cap",
    )


def _build_shelf_gusset_linear(params: ToolShelfParams, derived: Derived):
    if (
        not params.show_gusset
        or params.gusset_height <= 0
        or derived.gusset_a1 <= derived.gusset_a0
        or derived.gusset_r1 <= derived.gusset_r0 + 0.2
    ):
        return None

    top_r1 = min(derived.gusset_r1, derived.gusset_r0 + derived.gusset_top_flat_eff)
    if top_r1 <= derived.gusset_r0 + 0.05:
        return None

    top_points = _annular_sector_points(
        derived.gusset_r0,
        derived.gusset_r1,
        derived.gusset_a0,
        derived.gusset_a1,
        -derived.mount_wall_radius,
    )
    bottom_points = _annular_sector_points(
        derived.gusset_r0,
        top_r1,
        derived.gusset_a0,
        derived.gusset_a1,
        -derived.mount_wall_radius,
    )

    with BuildPart() as gusset:
        # Flip the v1 gusset direction: wide at shelf underside, narrow at the lower edge.
        with BuildSketch(Plane.XY.offset(-params.floor_thickness)):
            with BuildLine():
                Polyline(*top_points, close=True)
            make_face()
        with BuildSketch(Plane.XY.offset(-params.floor_thickness - params.gusset_height)):
            with BuildLine():
                Polyline(*bottom_points, close=True)
            make_face()
        loft(ruled=True)

    return gusset.part


def _build_drain_notch_cut(params: ToolShelfParams, derived: Derived):
    if not params.enable_drain_notch or params.lip_height_far <= 0 or params.lip_thickness <= 0 or params.drain_notch_width <= 0:
        return None
    notch_x0 = -derived.mount_wall_radius + derived.inner_radius - 0.5
    notch_w = params.lip_thickness + 1.0
    notch_h = params.lip_height_far + params.floor_thickness + 1.0
    notch_z0 = -params.floor_thickness - 0.5

    return Box(
        notch_w,
        params.drain_notch_width,
        notch_h,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    ).translate((notch_x0, 0.0, notch_z0))


def _build_clamp_channel_cut(params: ToolShelfParams, derived: Derived):
    if (
        not params.enable_clamp_channel
        or params.clamp_channel_depth <= 0
        or params.clamp_channel_width <= 0
        or params.clamp_cap_width <= 0
    ):
        return None

    channel_r1 = min(derived.outer_radius, derived.inner_radius + params.clamp_cap_width)
    channel_w = max(0.1, channel_r1 - derived.inner_radius)
    channel_x0 = -derived.mount_wall_radius + derived.inner_radius
    channel_z0 = max(0.0, params.clamp_cap_thickness - params.clamp_channel_depth)

    return Box(
        channel_w,
        params.clamp_channel_width,
        params.clamp_channel_depth + 0.5,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    ).translate((channel_x0, params.clamp_channel_offset, channel_z0))


def build_shelf_linear(params: ToolShelfParams, derived: Derived):
    parts = []
    floor = _build_shelf_floor_linear(params, derived)
    if floor is not None:
        parts.append(floor)

    if params.show_lips:
        parts.extend(_build_shelf_lips_linear(params, derived))

    clamp_cap = _build_shelf_clamp_cap_linear(params, derived)
    if clamp_cap is not None:
        parts.append(clamp_cap)

    gusset = _build_shelf_gusset_linear(params, derived)
    if gusset is not None:
        parts.append(gusset)

    if not parts:
        raise ValueError("Shelf geometry is empty with current parameters.")

    shelf = parts[0]
    for piece in parts[1:]:
        shelf = shelf + piece

    drain_cut = _build_drain_notch_cut(params, derived)
    if drain_cut is not None:
        shelf = shelf - drain_cut

    channel_cut = _build_clamp_channel_cut(params, derived)
    if channel_cut is not None:
        shelf = shelf - channel_cut

    mask_r_in = max(0.05, derived.mask_r_in)
    mask = _build_annular_sector_prism(
        mask_r_in,
        derived.mask_r_out,
        derived.a_start,
        derived.a_end,
        z0=derived.mask_z0,
        height=derived.mask_height,
        axis_r=derived.mount_wall_radius,
    )
    if mask is not None:
        shelf = shelf.intersect(mask)
    return shelf


def attachment_frame(part, angle_deg: float, radial_r: float, profile_y: float, tangent: float = 0.0):
    return part.translate((radial_r, tangent, profile_y)).rotate(Axis.Z, angle_deg).rotate(Axis.X, 90.0)


def build_assembly(params: ToolShelfParams, profile: CClampProfile, holder_only: bool):
    derived = derive(params, profile)

    if holder_only:
        shelf_only = build_shelf_linear(params, derived).rotate(Axis.Y, -params.holder_tilt_deg)
        return shelf_only, derived

    parts = []
    clamp_pad_sweep = build_clamp_pad_sweep(params, profile, derived)
    if clamp_pad_sweep is not None:
        parts.append(clamp_pad_sweep)

    if params.show_shelf:
        shelf_positioned = build_shelf_linear(params, derived).rotate(Axis.Y, -params.holder_tilt_deg)
        shelf_positioned = attachment_frame(
            shelf_positioned,
            derived.attach_angle,
            derived.mount_wall_radius,
            derived.holder_profile_y_sweep,
            0.0,
        )
        parts.append(shelf_positioned)

    if not parts:
        raise ValueError("Both clamp/pad and shelf are disabled; nothing to build.")

    model = parts[0]
    for piece in parts[1:]:
        model = model + piece
    return model, derived


def print_checks(params: ToolShelfParams, derived: Derived) -> None:
    print(f"INFO: arc_length_in = {params.arc_length / 25.4:.3f}")
    print(f"INFO: radial_width_in = {params.radial_width / 25.4:.3f}")
    print(f"INFO: arc_length_effective_in = {derived.arc_length_effective / 25.4:.3f}")
    print(f"INFO: footprint_mm = ({derived.footprint_x:.2f}, {derived.footprint_y:.2f})")
    print(f"INFO: footprint_in = ({derived.footprint_x / 25.4:.3f}, {derived.footprint_y / 25.4:.3f})")

    if derived.projection_from_pad_outer > params.max_projection:
        print("WARNING: projection exceeds max_projection.")
    if params.floor_thickness < params.min_floor_thickness_recommended:
        print("WARNING: floor_thickness is thin for PLA/PETG.")
    if params.lip_thickness < params.min_lip_thickness_recommended:
        print("WARNING: lip_thickness is thin for PLA/PETG.")
    if params.gusset_thickness < params.min_gusset_thickness_recommended:
        print("WARNING: gusset_thickness is thin for PLA/PETG.")
    if params.gusset_height < params.min_gusset_height_recommended:
        print("WARNING: gusset_height is low for wet loads.")
    if params.holder_radial_location_on_pad < 0 or params.holder_radial_location_on_pad > params.pad_length:
        print("WARNING: holder_radial_location_on_pad is outside pad_length.")
    if derived.inner_radius <= 0 or derived.outer_radius <= derived.inner_radius or derived.shelf_angle_deg <= 0:
        print("WARNING: invalid annular-sector geometry.")
    if params.align_to_sweep_edges and abs(params.holder_angle_offset) > 0.01:
        print("WARNING: holder_angle_offset breaks sweep-edge alignment.")
    if params.align_to_sweep_edges and abs(derived.arc_length_effective - params.arc_length) > 0.5:
        print("WARNING: arc_length differs from sweep-aligned effective arc length.")
    if derived.gusset_base_span + 0.1 < derived.gusset_base_min:
        print("WARNING: gusset slope may be steep for side printing.")
    if derived.gusset_r1 <= derived.gusset_r0 + 0.2:
        print("WARNING: gusset span collapsed; check gusset dimensions.")
    if max(params.lip_height_far, params.lip_height_sides) > params.mount_flat_wall_height_available + 5:
        print("WARNING: lip heights may interfere with clamp region.")
    if derived.footprint_x > params.ender3_v3_bed_x or derived.footprint_y > params.ender3_v3_bed_y:
        print("WARNING: footprint exceeds 220x220 bed.")


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
    parser = argparse.ArgumentParser(description="build123d tool shelf v2 (ported from v1 SCAD).")
    parser.add_argument(
        "--output",
        "-o",
        default=str(DEFAULT_OUTPUT),
        help=f"Output STL path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--holder-only",
        action="store_true",
        help="Render holder-only sample orientation for fast test prints",
    )
    parser.add_argument(
        "--attachment-support",
        action=argparse.BooleanOptionalAction,
        default=PRIMARY_ATTACHMENT_SUPPORT_ENABLED,
        help="Enable attachment support stub (pad). Disable to keep back wall as outermost edge.",
    )
    parser.add_argument(
        "--clamp-back-wall-stretch",
        type=float,
        default=PRIMARY_CLAMP_BACK_WALL_STRETCH_MM,
        help="Stretch C-clamp by lengthening from middle of straight back wall (mm, default: 0.0)",
    )
    default_preview = len(sys.argv) == 1
    parser.add_argument(
        "--preview",
        action="store_true",
        default=default_preview,
        help="Show preview in OCP CAD Viewer and skip STL export unless --export is also set",
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
        holder_only=args.holder_only,
        clamp_back_wall_stretch=args.clamp_back_wall_stretch,
        attachment_support=args.attachment_support,
        preview=args.preview,
        export=args.export,
    )


def runtime_from_head_config() -> RuntimeOptions:
    return RuntimeOptions(
        output=Path(HEAD_OUTPUT),
        holder_only=HEAD_HOLDER_ONLY,
        clamp_back_wall_stretch=PRIMARY_CLAMP_BACK_WALL_STRETCH_MM,
        attachment_support=PRIMARY_ATTACHMENT_SUPPORT_ENABLED,
        preview=HEAD_PREVIEW,
        export=HEAD_EXPORT,
    )


def main() -> int:
    run = runtime_from_head_config() if USE_HEAD_CONFIG else runtime_from_args(parse_args())
    params = ToolShelfParams(
        render_holder_only=run.holder_only,
        clamp_back_wall_stretch=run.clamp_back_wall_stretch,
        enable_attachment_support=run.attachment_support,
    )
    profile = load_c_clamp_profile()
    profile = stretch_profile_from_back_wall_mid(profile, params.clamp_back_wall_stretch)
    if abs(params.clamp_back_wall_stretch) > 1e-9:
        print(f"INFO: clamp back-wall stretch applied from mid-wall: {params.clamp_back_wall_stretch:.3f} mm")
    if not params.enable_attachment_support:
        print("INFO: attachment support disabled; back wall is outermost clamp edge.")

    model, derived = build_assembly(params, profile, holder_only=run.holder_only or params.render_holder_only)
    print_checks(params, derived)
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
