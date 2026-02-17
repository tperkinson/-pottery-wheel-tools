#!/usr/bin/env python3
"""build123d port of attachments/throwing_water_holder/v2/throwing_water_holder_v2c.scad."""

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
        BuildLine,
        BuildPart,
        BuildSketch,
        GeomType,
        Locations,
        Plane,
        Polyline,
        Rectangle,
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
DEFAULT_OUTPUT = REPO_ROOT / "build/throwing_water_holder_v3_b123d.stl"
PRIMARY_CLAMP_BACK_WALL_STRETCH_MM = 0.0
PRIMARY_ATTACHMENT_SUPPORT_ENABLED = True

# -------------------------------------------------
# Run Config (alternative to argparse)
# Set USE_HEAD_CONFIG = True to run using constants below.
# -------------------------------------------------
USE_HEAD_CONFIG = False
HEAD_PREVIEW = False
HEAD_EXPORT = True
HEAD_OUTPUT = DEFAULT_OUTPUT
HEAD_HOLDER_ONLY = False
HEAD_ALIGN_FLOOR_TO_CLAMP_BOTTOM = False
HEAD_FLOOR_CLAMP_CLEARANCE = 0.0
HEAD_PRINT_BED = False
HEAD_CLIP_MOUNT_INTRUSION = True
HEAD_MOUNT_INTRUSION_CLIP_CLEARANCE = 0.2


@dataclass(frozen=True)
class RuntimeOptions:
    output: Path
    holder_only: bool
    clamp_back_wall_stretch: float
    attachment_support: bool
    align_floor_to_clamp_bottom: bool
    floor_clamp_clearance: float
    print_bed: bool
    clip_mount_intrusion: bool
    mount_intrusion_clip_clearance: float
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
class ThrowingWaterHolderParams:
    # -------------------------------
    # Quick Tuning
    # -------------------------------
    holder_only_side_print: bool = True
    show_clamp: bool = True
    show_pad: bool = True
    enable_attachment_support: bool = PRIMARY_ATTACHMENT_SUPPORT_ENABLED
    show_holder: bool = True
    radius: float = 222.25
    radius_ref_mode: str = "hook_center"
    axis_z: float = 0.0
    clamp_back_wall_stretch: float = PRIMARY_CLAMP_BACK_WALL_STRETCH_MM
    sweep_angle: float = 24.0
    pad_length: float = 8.0
    pad_thickness: float = 4.0
    pad_overlap: float = 1.0
    pad_offset_y: float = 0.0
    holder_top_offset: float = 16.0
    align_floor_to_clamp_bottom: bool = False
    floor_to_clamp_bottom_clearance: float = 0.0
    holder_tilt_deg: float = 0.0
    holder_angle_offset: float = 0.0
    holder_radial_location_on_pad: float = 0.0
    shared_wall_overlap: float = 1.5
    clip_mount_intrusion_from_interior: bool = True
    mount_intrusion_clip_clearance: float = 0.2
    match_side_walls_to_sweep: bool = True
    side_start_deg: float = 0.0
    side_span_manual_deg: float = 0.0
    side_wall_sweep_margin_deg: float = 0.0
    target_volume_ml: float = 946.0
    volume_headroom_ml: float = 120.0
    arc_length: float = 102.0
    radial_width: float = 135.0
    depth: float = 72.0
    back_wall_height: float = 72.0
    front_wall_height: float = 72.0

    # -------------------------------
    # Strength / Printability
    # -------------------------------
    wall_thickness: float = 4.8
    floor_thickness: float = 4.5

    # -------------------------------
    # Advanced Controls
    # -------------------------------
    plan_corner_round_radius: float = 8.0
    interior_floor_blend_radius: float = 4.0
    top_edge_round_radius: float = 2.2
    shell_round_target_radius: float = 12.0
    front_rim_round_radius: float = 2.2
    back_rim_round_radius: float = 2.2
    side_top_round_radius: float = 2.2
    front_side_corner_round_radius: float = 2.2
    back_side_corner_round_radius: float = 2.2
    max_projection: float = 127.0
    ender3_v3_bed_x: float = 220.0
    ender3_v3_bed_y: float = 220.0


@dataclass(frozen=True)
class Derived:
    # -------------------------------
    # Derived values
    # -------------------------------
    radius_ref_x: float
    axis_x: float
    axis_shift_x: float
    holder_origin_x: float
    holder_top_offset_eff: float
    holder_profile_y_2d: float
    holder_profile_y_sweep: float
    floor_to_clamp_bottom_delta: float
    holder_r: float
    attach_angle: float
    side_span_from_arc_length_deg: float
    side_span_deg: float
    a_start: float
    a_end: float
    r_front_outer: float
    r_back_outer: float
    r_front_inner: float
    r_back_inner: float
    r_mid_inner: float
    side_wall_angle_thickness_deg: float
    a_inner_start: float
    a_inner_end: float
    floor_blend_radius: float
    plan_corner_round_outer: float
    plan_corner_round_inner: float
    front_wall_height_eff: float
    inner_height_fill: float
    inner_height_max: float
    max_safe_top_round: float
    angle_rad: float
    inner_plan_area_mm2: float
    fill_volume_ml_est: float
    max_volume_ml_est: float
    back_arc_length: float
    projection_from_pad_outer: float
    holder_footprint_x: float
    holder_footprint_y: float


def smoothstep01(t: float) -> float:
    if t <= 0:
        return 0.0
    if t >= 1:
        return 1.0
    return t * t * (3.0 - 2.0 * t)


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


def derive(params: ThrowingWaterHolderParams, profile: CClampProfile) -> Derived:
    radius_ref_x = profile.hook_center_x if params.radius_ref_mode == "hook_center" else profile.max_profile_x
    axis_x = radius_ref_x - params.radius
    axis_shift_x = max(0.0, axis_x - profile.min_profile_x + 0.1)

    holder_origin_x = profile.max_profile_x + params.holder_radial_location_on_pad
    if params.align_floor_to_clamp_bottom:
        holder_top_offset_eff = (
            profile.min_profile_y - profile.max_profile_y + params.back_wall_height + params.floor_to_clamp_bottom_clearance
        )
    else:
        holder_top_offset_eff = params.holder_top_offset
    holder_profile_y_2d = profile.max_profile_y + holder_top_offset_eff
    holder_profile_y_sweep = holder_profile_y_2d - params.axis_z
    floor_to_clamp_bottom_delta = (
        holder_profile_y_2d - params.back_wall_height
    ) - profile.min_profile_y
    holder_r = axis_shift_x + (holder_origin_x - axis_x)
    attach_angle = params.holder_angle_offset

    side_span_from_arc_length_deg = (params.arc_length / holder_r) * 180.0 / math.pi if holder_r > 0 else 0.0
    side_span_base_deg = params.side_span_manual_deg if params.side_span_manual_deg > 0 else side_span_from_arc_length_deg
    side_span_deg = (
        params.sweep_angle if params.match_side_walls_to_sweep else side_span_base_deg
    ) + params.side_wall_sweep_margin_deg
    a_start = 0.0 if params.match_side_walls_to_sweep else params.side_start_deg
    a_end = a_start + side_span_deg

    r_front_outer = holder_r - params.shared_wall_overlap
    r_back_outer = r_front_outer + params.radial_width
    r_front_inner = r_front_outer + params.wall_thickness
    r_back_inner = r_back_outer - params.wall_thickness
    r_mid_inner = max(0.1, (r_front_inner + r_back_inner) / 2.0)
    side_wall_angle_thickness_deg = (params.wall_thickness / r_mid_inner) * 180.0 / math.pi
    a_inner_start = a_start + side_wall_angle_thickness_deg
    a_inner_end = a_end - side_wall_angle_thickness_deg

    floor_blend_radius = min(
        params.interior_floor_blend_radius,
        max(0.5, params.wall_thickness - 0.4),
        max(0.5, (r_back_inner - r_front_inner) / 4.0),
        max(0.5, (params.back_wall_height - params.floor_thickness) / 3.0),
    )

    plan_corner_round_outer = max(0.0, params.plan_corner_round_radius)
    plan_corner_round_inner = max(0.0, plan_corner_round_outer - params.wall_thickness)

    front_wall_height_eff = min(
        params.back_wall_height - 0.1,
        max(params.floor_thickness + 1.0, params.front_wall_height),
    )
    inner_height_fill = max(0.0, front_wall_height_eff - params.floor_thickness)
    inner_height_max = max(0.0, params.back_wall_height - params.floor_thickness)
    max_safe_top_round = max(0.0, params.wall_thickness * 0.55)

    angle_rad = max(0.0, (a_inner_end - a_inner_start) * math.pi / 180.0)
    if r_back_inner > r_front_inner and angle_rad > 0:
        inner_plan_area_mm2 = 0.5 * angle_rad * (r_back_inner**2 - r_front_inner**2)
    else:
        inner_plan_area_mm2 = 0.0
    fill_volume_ml_est = inner_plan_area_mm2 * inner_height_fill / 1000.0
    max_volume_ml_est = inner_plan_area_mm2 * inner_height_max / 1000.0
    back_arc_length = r_back_outer * angle_rad

    pad_outer_local_x = params.pad_length - params.holder_radial_location_on_pad
    projection_from_pad_outer = (r_back_outer - holder_r) - pad_outer_local_x
    holder_footprint_x = params.radial_width
    holder_footprint_y = back_arc_length

    return Derived(
        radius_ref_x=radius_ref_x,
        axis_x=axis_x,
        axis_shift_x=axis_shift_x,
        holder_origin_x=holder_origin_x,
        holder_top_offset_eff=holder_top_offset_eff,
        holder_profile_y_2d=holder_profile_y_2d,
        holder_profile_y_sweep=holder_profile_y_sweep,
        floor_to_clamp_bottom_delta=floor_to_clamp_bottom_delta,
        holder_r=holder_r,
        attach_angle=attach_angle,
        side_span_from_arc_length_deg=side_span_from_arc_length_deg,
        side_span_deg=side_span_deg,
        a_start=a_start,
        a_end=a_end,
        r_front_outer=r_front_outer,
        r_back_outer=r_back_outer,
        r_front_inner=r_front_inner,
        r_back_inner=r_back_inner,
        r_mid_inner=r_mid_inner,
        side_wall_angle_thickness_deg=side_wall_angle_thickness_deg,
        a_inner_start=a_inner_start,
        a_inner_end=a_inner_end,
        floor_blend_radius=floor_blend_radius,
        plan_corner_round_outer=plan_corner_round_outer,
        plan_corner_round_inner=plan_corner_round_inner,
        front_wall_height_eff=front_wall_height_eff,
        inner_height_fill=inner_height_fill,
        inner_height_max=inner_height_max,
        max_safe_top_round=max_safe_top_round,
        angle_rad=angle_rad,
        inner_plan_area_mm2=inner_plan_area_mm2,
        fill_volume_ml_est=fill_volume_ml_est,
        max_volume_ml_est=max_volume_ml_est,
        back_arc_length=back_arc_length,
        projection_from_pad_outer=projection_from_pad_outer,
        holder_footprint_x=holder_footprint_x,
        holder_footprint_y=holder_footprint_y,
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


def _make_annular_sector(
    r_inner: float,
    r_outer: float,
    a_start_deg: float,
    a_end_deg: float,
    z0: float,
    height: float,
):
    span = a_end_deg - a_start_deg
    if r_outer <= r_inner or height <= 0 or span <= 0:
        raise ValueError("Invalid annular sector dimensions.")

    with BuildPart() as part:
        with BuildSketch(Plane.XZ):
            with Locations((r_inner, z0 + height / 2.0)):
                Rectangle(r_outer - r_inner, height, align=(Align.MIN, Align.CENTER))
        revolve(axis=Axis.Z, revolution_arc=span)

    return part.part.rotate(Axis.Z, a_start_deg)


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


def _constant_z_edges(part, z_value: float, tol: float = 0.1) -> list:
    return [
        edge
        for edge in part.edges()
        if abs(edge.bounding_box().min.Z - z_value) <= tol and abs(edge.bounding_box().max.Z - z_value) <= tol
    ]


def _deg_dist(a: float, b: float) -> float:
    d = abs((a - b) % 360.0)
    return min(d, 360.0 - d)


def _outer_side_floor_edges(part, derived: Derived) -> list:
    edges = []
    for edge in _constant_z_edges(part, 0.0, tol=0.15):
        if edge.geom_type != GeomType.LINE:
            continue
        mid = edge.position_at(0.5)
        ang = (math.degrees(math.atan2(mid.Y, mid.X)) + 360.0) % 360.0
        if min(_deg_dist(ang, derived.a_start), _deg_dist(ang, derived.a_end)) < 1.5:
            edges.append(edge)
    return edges


def build_clamp_pad_sweep(params: ThrowingWaterHolderParams, profile: CClampProfile, derived: Derived):
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


def _build_top_taper_cutter(params: ThrowingWaterHolderParams, derived: Derived):
    if params.back_wall_height <= derived.front_wall_height_eff + 0.05:
        return None

    steps = 16
    r0 = max(0.1, derived.r_front_outer - 2.0 * params.wall_thickness)
    r1 = derived.r_back_outer + 2.0 * params.wall_thickness
    z_cap = params.back_wall_height + max(12.0, params.side_top_round_radius + params.back_rim_round_radius)
    span_r = max(0.1, derived.r_back_outer - derived.r_front_outer)

    top_profile_pts: list[tuple[float, float]] = [(r0, derived.front_wall_height_eff)]
    for i in range(1, steps + 1):
        t = i / steps
        rr = r0 + (r1 - r0) * t
        blend = smoothstep01((rr - derived.r_front_outer) / span_r)
        zz = derived.front_wall_height_eff + (params.back_wall_height - derived.front_wall_height_eff) * blend
        top_profile_pts.append((rr, zz))
    top_profile_pts.extend([(r1, z_cap), (r0, z_cap)])

    return _revolve_closed_profile(top_profile_pts, derived.a_end - derived.a_start, start_angle=derived.a_start)


def build_holder_linear(params: ThrowingWaterHolderParams, derived: Derived):
    outer = _make_annular_sector(
        derived.r_front_outer,
        derived.r_back_outer,
        derived.a_start,
        derived.a_end,
        z0=0.0,
        height=params.back_wall_height,
    )
    outer = _safe_fillet(
        outer,
        list(outer.edges().filter_by(Axis.Z)),
        derived.plan_corner_round_outer,
        "outer_plan_corner",
    )

    inner_cut_height = max(1.0, params.back_wall_height - params.floor_thickness + 30.0)
    inner = _make_annular_sector(
        derived.r_front_inner,
        derived.r_back_inner,
        derived.a_inner_start,
        derived.a_inner_end,
        z0=params.floor_thickness,
        height=inner_cut_height,
    )
    inner = _safe_fillet(
        inner,
        list(inner.edges().filter_by(Axis.Z)),
        derived.plan_corner_round_inner,
        "inner_plan_corner",
    )

    holder = outer - inner

    top_cutter = _build_top_taper_cutter(params, derived)
    if top_cutter is not None:
        holder = holder - top_cutter

    holder = _safe_fillet(
        holder,
        _constant_z_edges(holder, params.floor_thickness),
        derived.floor_blend_radius,
        "interior_floor_blend",
    )
    outer_side_floor_r = min(derived.floor_blend_radius, params.wall_thickness * 0.6)
    holder = _safe_fillet(
        holder,
        _outer_side_floor_edges(holder, derived),
        outer_side_floor_r,
        "outer_side_floor_blend",
    )

    top_round = min(params.top_edge_round_radius, derived.max_safe_top_round)
    top_edges = _constant_z_edges(holder, derived.front_wall_height_eff, tol=0.2)
    top_edges.extend(_constant_z_edges(holder, params.back_wall_height, tol=0.2))
    # Deduplicate shape handles before fillet.
    top_edges = list(dict.fromkeys(top_edges))
    holder = _safe_fillet(holder, top_edges, top_round, "top_edge_round")

    # Match SCAD local frame where holder body is centered at x = -holder_r before placement.
    return holder.translate((-derived.holder_r, 0.0, 0.0))


def build_interior_keepout_linear(params: ThrowingWaterHolderParams, derived: Derived):
    clear = max(0.0, params.mount_intrusion_clip_clearance)
    angular_clear = (clear / derived.r_mid_inner) * 180.0 / math.pi if derived.r_mid_inner > 0 else 0.0

    r_inner = derived.r_front_inner + clear
    r_outer = derived.r_back_inner - clear
    a_start = derived.a_inner_start + angular_clear
    a_end = derived.a_inner_end - angular_clear
    z0 = params.floor_thickness + clear
    height = max(0.2, params.back_wall_height - params.floor_thickness + 2.0 - clear)

    if r_outer <= r_inner + 0.2 or a_end <= a_start + 0.2:
        return None

    keepout = _make_annular_sector(
        r_inner,
        r_outer,
        a_start,
        a_end,
        z0=z0,
        height=height,
    )
    return keepout.translate((-derived.holder_r, 0.0, 0.0))


def attachment_frame(part, angle_deg: float, radial_r: float, profile_y: float, tangent: float = 0.0):
    return part.translate((radial_r, tangent, profile_y)).rotate(Axis.Z, angle_deg).rotate(Axis.X, 90.0)


def build_assembly(
    params: ThrowingWaterHolderParams,
    profile: CClampProfile,
    holder_only: bool,
):
    derived = derive(params, profile)

    holder_linear = build_holder_linear(params, derived)
    interior_keepout_linear = (
        build_interior_keepout_linear(params, derived)
        if params.clip_mount_intrusion_from_interior and params.show_holder
        else None
    )
    holder_local_placed = holder_linear.translate((0.0, 0.0, -params.back_wall_height))
    keepout_local_placed = (
        interior_keepout_linear.translate((0.0, 0.0, -params.back_wall_height))
        if interior_keepout_linear is not None
        else None
    )

    if holder_only:
        if params.holder_only_side_print:
            model = holder_local_placed.rotate(Axis.Y, 90.0)
            keepout = keepout_local_placed.rotate(Axis.Y, 90.0) if keepout_local_placed is not None else None
        else:
            model = holder_local_placed.rotate(Axis.Y, -params.holder_tilt_deg)
            keepout = (
                keepout_local_placed.rotate(Axis.Y, -params.holder_tilt_deg)
                if keepout_local_placed is not None
                else None
            )
        if keepout is not None:
            model = model - keepout
        return model, derived

    holder_positioned = holder_local_placed.rotate(Axis.Y, -params.holder_tilt_deg)
    holder_positioned = attachment_frame(
        holder_positioned,
        derived.attach_angle,
        derived.holder_r,
        derived.holder_profile_y_sweep,
        0.0,
    )
    keepout_positioned = None
    if keepout_local_placed is not None:
        keepout_positioned = keepout_local_placed.rotate(Axis.Y, -params.holder_tilt_deg)
        keepout_positioned = attachment_frame(
            keepout_positioned,
            derived.attach_angle,
            derived.holder_r,
            derived.holder_profile_y_sweep,
            0.0,
        )

    parts = []
    clamp_pad_sweep = build_clamp_pad_sweep(params, profile, derived)
    if clamp_pad_sweep is not None:
        parts.append(clamp_pad_sweep)
    if params.show_holder:
        parts.append(holder_positioned)

    if not parts:
        raise ValueError("Both holder and clamp/pad are disabled; nothing to build.")

    model = parts[0]
    for piece in parts[1:]:
        model = model + piece
    if keepout_positioned is not None:
        model = model - keepout_positioned
    return model, derived


def print_checks(params: ThrowingWaterHolderParams, derived: Derived) -> None:
    print(
        "INFO: holder_top_offset effective (mm) = "
        f"{derived.holder_top_offset_eff:.3f}"
        + (
            " (auto aligned to clamp bottom)"
            if params.align_floor_to_clamp_bottom
            else ""
        )
    )
    print(
        "INFO: mount intrusion clipping = "
        + (
            f"enabled (clearance={params.mount_intrusion_clip_clearance:.3f} mm)"
            if params.clip_mount_intrusion_from_interior
            else "disabled"
        )
    )
    print(f"INFO: floor minus clamp-bottom delta (mm) = {derived.floor_to_clamp_bottom_delta:.3f}")
    print(f"INFO: fill-line volume estimate (ml) = {derived.fill_volume_ml_est:.1f}")
    print(f"INFO: max volume estimate (ml) = {derived.max_volume_ml_est:.1f}")
    print(f"INFO: side angles (deg) = [{derived.a_start:.3f}, {derived.a_end:.3f}]")

    if params.wall_thickness < 3.0:
        print("WARNING: wall_thickness < 3.0 mm may be weak.")
    if params.floor_thickness < 3.8:
        print("WARNING: floor_thickness < 3.8 mm may be weak.")
    if derived.r_front_inner <= 0 or derived.r_back_inner <= derived.r_front_inner:
        print("WARNING: invalid annular basin radii.")
    if derived.a_end <= derived.a_start:
        print("WARNING: invalid side wall angles.")
    if derived.a_inner_end <= derived.a_inner_start:
        print("WARNING: side-wall thickness too large for current angular span.")
    if derived.front_wall_height_eff <= params.floor_thickness:
        print("WARNING: front wall height must exceed floor thickness.")
    if derived.projection_from_pad_outer > params.max_projection:
        print("WARNING: projection exceeds max_projection.")
    if derived.fill_volume_ml_est < params.target_volume_ml:
        print("WARNING: fill-line volume below target_volume_ml.")
    if derived.max_volume_ml_est < params.target_volume_ml + params.volume_headroom_ml:
        print("WARNING: max volume below target_volume_ml + volume_headroom_ml.")
    if params.match_side_walls_to_sweep and abs(params.side_start_deg) > 0.01:
        print("WARNING: side_start_deg != 0 while sweep-match is enabled.")
    if params.match_side_walls_to_sweep and abs(derived.side_span_from_arc_length_deg - params.sweep_angle) > 3.0:
        print("WARNING: arc_length-implied angle differs from sweep_angle by >3 deg.")
    if derived.a_end > params.sweep_angle + 0.01:
        print("WARNING: side-end exceeds sweep angle; holder may extend beyond clamp sweep.")
    if params.plan_corner_round_radius > (params.radial_width / 2.0):
        print("WARNING: plan_corner_round_radius too large for radial_width.")
    if params.front_rim_round_radius > derived.front_wall_height_eff - params.floor_thickness:
        print("WARNING: front_rim_round_radius too large for front wall.")
    if params.back_rim_round_radius > params.back_wall_height - params.floor_thickness:
        print("WARNING: back_rim_round_radius too large for back wall.")
    if params.side_top_round_radius > (params.back_wall_height - params.floor_thickness):
        print("WARNING: side_top_round_radius too large for side wall height.")
    if params.front_side_corner_round_radius > (derived.front_wall_height_eff - params.floor_thickness):
        print("WARNING: front_side_corner_round_radius too large for front corners.")
    if params.back_side_corner_round_radius > (params.back_wall_height - params.floor_thickness):
        print("WARNING: back_side_corner_round_radius too large for back corners.")
    if params.top_edge_round_radius < 0.4:
        print("WARNING: top_edge_round_radius too small; rim and top-corner seams may remain sharp.")
    if derived.floor_blend_radius < 0.4:
        print("WARNING: floor_blend_radius too small; floor seams may remain sharp.")
    if (
        derived.holder_footprint_x > params.ender3_v3_bed_x
        or derived.holder_footprint_y > params.ender3_v3_bed_y
    ):
        print("WARNING: holder-only footprint likely exceeds Ender 3 V3 bed (220x220 mm).")


def print_geometry_summary(model, derived: Derived) -> None:
    bb = model.bounding_box()
    size = bb.size
    print(
        "SUMMARY: bbox_min=(%.2f, %.2f, %.2f) bbox_max=(%.2f, %.2f, %.2f) size=(%.2f, %.2f, %.2f) mm"
        % (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z, size.X, size.Y, size.Z)
    )
    print(f"SUMMARY: CAD volume estimate = {model.volume / 1000.0:.1f} ml")
    print(f"SUMMARY: fill-line / max volume estimates = {derived.fill_volume_ml_est:.1f} / {derived.max_volume_ml_est:.1f} ml")


def orient_for_print_bed(part):
    oriented = part.rotate(Axis.X, -90.0)
    bb = oriented.bounding_box()
    return oriented.translate((0.0, 0.0, -bb.min.Z))


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
    parser = argparse.ArgumentParser(description="build123d throwing water holder v3 (ported from v2c SCAD).")
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
    parser.add_argument(
        "--align-floor-to-clamp-bottom",
        action="store_true",
        help="Auto-set holder_top_offset so holder floor aligns to clamp profile bottom",
    )
    parser.add_argument(
        "--floor-clamp-clearance",
        type=float,
        default=0.0,
        help="Extra offset (mm) added when --align-floor-to-clamp-bottom is set (default: 0.0)",
    )
    parser.add_argument(
        "--print-bed",
        action="store_true",
        help="Rotate exported/previewed model for print bed orientation and shift so min Z=0",
    )
    parser.add_argument(
        "--clip-mount-intrusion",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Clip any clamp/pad intrusion that enters the holder interior (default: enabled)",
    )
    parser.add_argument(
        "--mount-intrusion-clip-clearance",
        type=float,
        default=0.2,
        help="Interior keepout inset (mm) used by mount-intrusion clipping (default: 0.2)",
    )
    # VS Code "Run Python File" passes no args; default that path to preview.
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
        align_floor_to_clamp_bottom=args.align_floor_to_clamp_bottom,
        floor_clamp_clearance=args.floor_clamp_clearance,
        print_bed=args.print_bed,
        clip_mount_intrusion=args.clip_mount_intrusion,
        mount_intrusion_clip_clearance=args.mount_intrusion_clip_clearance,
        preview=args.preview,
        export=args.export,
    )


def runtime_from_head_config() -> RuntimeOptions:
    return RuntimeOptions(
        output=Path(HEAD_OUTPUT),
        holder_only=HEAD_HOLDER_ONLY,
        clamp_back_wall_stretch=PRIMARY_CLAMP_BACK_WALL_STRETCH_MM,
        attachment_support=PRIMARY_ATTACHMENT_SUPPORT_ENABLED,
        align_floor_to_clamp_bottom=HEAD_ALIGN_FLOOR_TO_CLAMP_BOTTOM,
        floor_clamp_clearance=HEAD_FLOOR_CLAMP_CLEARANCE,
        print_bed=HEAD_PRINT_BED,
        clip_mount_intrusion=HEAD_CLIP_MOUNT_INTRUSION,
        mount_intrusion_clip_clearance=HEAD_MOUNT_INTRUSION_CLIP_CLEARANCE,
        preview=HEAD_PREVIEW,
        export=HEAD_EXPORT,
    )


def main() -> int:
    run = runtime_from_head_config() if USE_HEAD_CONFIG else runtime_from_args(parse_args())
    params = ThrowingWaterHolderParams(
        clamp_back_wall_stretch=run.clamp_back_wall_stretch,
        enable_attachment_support=run.attachment_support,
        align_floor_to_clamp_bottom=run.align_floor_to_clamp_bottom,
        floor_to_clamp_bottom_clearance=run.floor_clamp_clearance,
        clip_mount_intrusion_from_interior=run.clip_mount_intrusion,
        mount_intrusion_clip_clearance=run.mount_intrusion_clip_clearance,
    )
    profile = load_c_clamp_profile()
    profile = stretch_profile_from_back_wall_mid(profile, params.clamp_back_wall_stretch)
    if abs(params.clamp_back_wall_stretch) > 1e-9:
        print(f"INFO: clamp back-wall stretch applied from mid-wall: {params.clamp_back_wall_stretch:.3f} mm")
    if not params.enable_attachment_support:
        print("INFO: attachment support disabled; back wall is outermost clamp edge.")

    model, derived = build_assembly(params, profile, holder_only=run.holder_only)
    if run.print_bed:
        model = orient_for_print_bed(model)
        print("INFO: applied --print-bed orientation (rotate X -90, then translate to Z=0).")
    print_checks(params, derived)
    print_geometry_summary(model, derived)

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
