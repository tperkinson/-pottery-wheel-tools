#!/usr/bin/env python3
"""Radial vertical rib shelf attachment (v1) in build123d."""

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
PRIMARY_SLOT_COUNT = 7
PRIMARY_SLOT_WIDTHS_MM = [3.0, 3.5, 4.0, 4.5, 5.5, 7.0, 9.0]
PRIMARY_SLOT_DEPTH_MM = 38.0
PRIMARY_SLOT_HEIGHT_MM = 31.5
PRIMARY_INNER_WALL_HEIGHT_MM = 24.0
PRIMARY_OUTER_WALL_HEIGHT_MM = 28.0
PRIMARY_INNER_WALL_LENGTH_MM = 34.0
PRIMARY_OUTER_WALL_LENGTH_MM = 42.0
PRIMARY_SLOT_PITCH_MM = 14.0
PRIMARY_RADIAL_WIDTH_MM = 102.0
PRIMARY_ARC_LENGTH_MM = 83.0
PRIMARY_FLOOR_THICKNESS_MM = 4.0
PRIMARY_WALL_THICKNESS_MM = 3.2
PRIMARY_DRAIN_CHANNEL_WIDTH_MM = 3.0
PRIMARY_DRAIN_CHANNEL_DEPTH_MM = 1.6
PRIMARY_TILT_DEG = 0.0
PRIMARY_MOUNT_CLOCK_POSITION = 4
PRIMARY_MATERIAL = "PLA"
PRIMARY_MOUNT_OVERLAP_MM = 16.0

PRIMARY_SWEEP_ANGLE_DEG = 20.0
PRIMARY_SWEEP_DIRECTION = 1  # +1: 0->+angle, -1: 0->-angle
PRIMARY_RADIUS_MM = 222.25
PRIMARY_PAD_LENGTH_MM = 12.0
PRIMARY_CLAMP_BACK_WALL_STRETCH_MM = 0.0

NOZZLE_DIAMETER_MM = 0.4

try:
    from build123d import (
        Align,
        Axis,
        Box,
        BuildLine,
        BuildPart,
        BuildSketch,
        Compound,
        Cylinder,
        Circle,
        Line,
        Locations,
        Plane,
        Polyline,
        ThreePointArc,
        ShapeList,
        export_stl,
        extrude,
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
DEFAULT_OUTPUT = REPO_ROOT / "build/rib_shelf_vertical_v1_b123d.stl"

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


@dataclass(frozen=True)
class CClampProfile:
    min_profile_x: float
    max_profile_x: float
    min_profile_y: float
    max_profile_y: float
    hook_center_x: float
    points: list[tuple[float, float]]


@dataclass(frozen=True)
class RibShelfParams:
    # -------------------------------
    # Quick Tuning
    # -------------------------------
    slot_count: int = PRIMARY_SLOT_COUNT
    slot_widths: tuple[float, ...] = tuple(PRIMARY_SLOT_WIDTHS_MM)
    slot_depth: float = PRIMARY_SLOT_DEPTH_MM
    slot_height: float = PRIMARY_SLOT_HEIGHT_MM
    inner_wall_height: float = PRIMARY_INNER_WALL_HEIGHT_MM
    outer_wall_height: float = PRIMARY_OUTER_WALL_HEIGHT_MM
    inner_wall_length: float = PRIMARY_INNER_WALL_LENGTH_MM
    outer_wall_length: float = PRIMARY_OUTER_WALL_LENGTH_MM
    slot_pitch: float = PRIMARY_SLOT_PITCH_MM
    radial_width: float = PRIMARY_RADIAL_WIDTH_MM
    arc_length: float = PRIMARY_ARC_LENGTH_MM
    floor_thickness: float = PRIMARY_FLOOR_THICKNESS_MM
    wall_thickness: float = PRIMARY_WALL_THICKNESS_MM
    drain_channel_width: float = PRIMARY_DRAIN_CHANNEL_WIDTH_MM
    drain_channel_depth: float = PRIMARY_DRAIN_CHANNEL_DEPTH_MM
    tilt_deg: float = PRIMARY_TILT_DEG
    mount_clock_position: int = PRIMARY_MOUNT_CLOCK_POSITION
    material: str = PRIMARY_MATERIAL

    sweep_angle: float = PRIMARY_SWEEP_ANGLE_DEG
    sweep_direction: int = PRIMARY_SWEEP_DIRECTION
    radius: float = PRIMARY_RADIUS_MM
    radius_ref_mode: str = "hook_center"
    axis_z: float = 0.0
    pad_length: float = PRIMARY_PAD_LENGTH_MM
    pad_thickness: float = 4.0
    pad_overlap: float = 1.0
    mount_overlap: float = PRIMARY_MOUNT_OVERLAP_MM
    pad_offset_y: float = 0.0
    clamp_back_wall_stretch: float = PRIMARY_CLAMP_BACK_WALL_STRETCH_MM
    shelf_top_offset: float = 0.0

    show_clamp: bool = True
    show_pad: bool = True
    show_shelf: bool = True

    # -------------------------------
    # Strength / Printability
    # -------------------------------
    min_wall_for_nozzle_multiplier: float = 3.0
    min_floor_recommended: float = 2.4
    min_drain_depth_recommended: float = 1.0
    max_projection: float = 127.0

    # -------------------------------
    # Advanced Controls
    # -------------------------------
    edge_fillet_radius: float = 0.9
    wall_floor_fillet_radius: float = 2.0
    slot_floor_scallop_max_radius: float = 3.0
    slot_floor_scallop_width_extra: float = 1.0
    slot_floor_scallop_edge_overrun: float = 1.2
    slot_edge_cleanup_band_width: float = 0.0
    slot_edge_cleanup_band_height: float = 0.0
    slot_edge_cleanup_band_z_drop: float = 0.35
    slot_edge_cleanup_band_outside_ratio: float = 0.25
    mount_underside_fillet_radius: float = 1.2
    show_wall_print_sweeps: bool = True
    wall_print_sweep_circle_cut: bool = True
    wall_print_scallop_cut_x_bleed: float = 0.2
    wall_print_scallop_cut_y_overshoot: float = 0.8
    wall_print_scallop_cut_z_overshoot: float = 0.3
    wall_print_scallop_edge_strip_width: float = 1.0
    wall_print_scallop_cut_start_z: float = 0.6
    wall_print_sweep_render_front_side: bool = True
    wall_print_sweep_render_back_side: bool = False
    wall_print_sweep_edge_inset: float = 0.0
    fragment_prune_max_volume_mm3: float = 0.10
    sweep_support_margin_deg: float = 0.5
    ender3_v3_bed_x: float = 220.0
    ender3_v3_bed_y: float = 220.0


@dataclass(frozen=True)
class Derived:
    radius_ref_x: float
    axis_x: float
    axis_shift_x: float
    mount_wall_radius: float
    pad_outer_radius: float
    inner_radius: float
    outer_radius: float
    centerline_radius: float
    sweep_angle_eff: float
    sweep_sign: float
    shelf_angle_deg: float
    attach_angle: float
    shelf_a_start: float
    shelf_a_end: float
    holder_top_z: float
    holder_profile_y_sweep: float
    floor_x_min: float
    floor_y_span: float
    slot_y_front: float
    slot_y_back: float
    lane_bounds: list[tuple[float, float]]
    divider_bounds: list[tuple[float, float]]
    lane_centers: list[float]
    lane_gaps_extra: list[float]
    total_lane_cluster_width: float
    wall_heights: list[float]
    wall_lengths: list[float]
    mask_z0: float
    mask_height: float
    intended_mount_clock_position: int


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


def _safe_fillet(part, edges: list, radius: float, label: str):
    if radius <= 0 or not edges:
        return part
    for scale in (1.0, 0.8, 0.6, 0.45):
        try_radius = radius * scale
        if try_radius < 0.15:
            continue
        try:
            if scale < 0.999:
                print(f"INFO: {label} fillet reduced from {radius:.2f} to {try_radius:.2f}")
            return part.fillet(try_radius, edges)
        except Exception:
            continue
    return part


def _coerce_single_shape(shape_obj, label: str):
    if not isinstance(shape_obj, ShapeList):
        return shape_obj
    shapes = list(shape_obj)
    if not shapes:
        raise ValueError(f"{label}: boolean operations produced no solids.")
    return shapes[0] if len(shapes) == 1 else Compound(shapes)


def _prune_tiny_detached_solids(shape_obj, max_volume_mm3: float, label: str):
    max_v = max(0.0, max_volume_mm3)
    if max_v <= 0.0:
        return shape_obj
    try:
        solids = list(shape_obj.solids())
    except Exception:
        return shape_obj
    if len(solids) <= 1:
        return shape_obj

    kept: list = []
    dropped_count = 0
    dropped_total = 0.0
    for solid in solids:
        vol = abs(float(solid.volume))
        if vol > max_v:
            kept.append(solid)
        else:
            dropped_count += 1
            dropped_total += vol

    if not kept:
        # Fallback safety: keep the largest solid if threshold would remove everything.
        kept = [max(solids, key=lambda s: abs(float(s.volume)))]
        dropped_count = max(0, len(solids) - 1)
        dropped_total = sum(abs(float(s.volume)) for s in solids if s is not kept[0])

    if dropped_count > 0:
        print(
            f"INFO: {label} pruned {dropped_count} tiny detached solids "
            f"(<= {max_v:.3f} mm^3, total {dropped_total:.4f} mm^3)."
        )
    if len(kept) == 1:
        return kept[0]
    return Compound(kept)


def _constant_z_edges(part, z_value: float, tol: float = 0.12) -> list:
    return [
        edge
        for edge in part.edges()
        if abs(edge.bounding_box().min.Z - z_value) <= tol and abs(edge.bounding_box().max.Z - z_value) <= tol
    ]


def _revolve_closed_profile(points_xz: list[tuple[float, float]], sweep_angle: float):
    with BuildPart() as part:
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Polyline(*points_xz, close=True)
            make_face()
        revolve(axis=Axis.Z, revolution_arc=sweep_angle)
    return part.part


def _seg_count_for_span(a0_deg: float, a1_deg: float) -> int:
    span = abs(a1_deg - a0_deg)
    return max(18, int(math.ceil(span / 2.2)) + 2)


def _arc_points(radius: float, a0_deg: float, a1_deg: float, n: int, x_center: float) -> list[tuple[float, float]]:
    if n < 2:
        n = 2
    points: list[tuple[float, float]] = []
    for i in range(n):
        t = i / (n - 1)
        ang = math.radians(a0_deg + (a1_deg - a0_deg) * t)
        points.append((x_center + radius * math.cos(ang), radius * math.sin(ang)))
    return points


def _annular_sector_points(
    r_in: float,
    r_out: float,
    a0_deg: float,
    a1_deg: float,
    x_center: float,
) -> list[tuple[float, float]]:
    n = _seg_count_for_span(a0_deg, a1_deg)
    outer = _arc_points(r_out, a0_deg, a1_deg, n, x_center)
    inner = _arc_points(r_in, a1_deg, a0_deg, n, x_center)
    return outer + inner


def _build_annular_sector_prism(
    r_in: float,
    r_out: float,
    a0_deg: float,
    a1_deg: float,
    z0: float,
    height: float,
    axis_r: float,
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
    return part.part


def _box_min(x: float, y: float, z: float, x0: float, y0: float, z0: float):
    return Box(x, y, z, align=(Align.MIN, Align.MIN, Align.MIN)).translate((x0, y0, z0))


def _box_center_minmax(x: float, y: float, z: float, cx: float, y0: float, z_top: float):
    return Box(x, y, z, align=(Align.CENTER, Align.MIN, Align.MAX)).translate((cx, y0, z_top))


def _build_single_wall_side_buttress(
    x0: float,
    x1: float,
    y_wall_edge: float,
    y_tray_side: float,
    z_floor: float,
    z_top: float,
    use_arc: bool,
    arc_fallback_to_straight: bool = True,
):
    x_span = x1 - x0
    y_span = abs(y_tray_side - y_wall_edge)
    z_span = z_top - z_floor
    if x_span <= 0.2 or y_span <= 0.2 or z_span <= 0.2:
        return None

    start = (y_wall_edge, z_top)
    end = (y_tray_side, z_floor)

    def _make(curved: bool):
        with BuildPart() as sweep:
            with BuildSketch(Plane.YZ):
                with BuildLine():
                    Line((y_tray_side, z_floor), (y_wall_edge, z_floor))
                    Line((y_wall_edge, z_floor), start)
                    if curved:
                        # Inward scoop ("circle-cut" feel) to reduce bulk near tray edge.
                        y_mid = y_wall_edge + (y_tray_side - y_wall_edge) * 0.65
                        z_mid = z_floor + (z_top - z_floor) * 0.24
                        ThreePointArc(start, (y_mid, z_mid), end)
                    else:
                        Line(start, end)
                make_face()
            extrude(amount=x_span)
        return sweep.part.translate((x0, 0.0, 0.0))

    if use_arc:
        try:
            return _make(True)
        except Exception:
            if not arc_fallback_to_straight:
                return None
    return _make(False)


def _build_wall_side_buttress_scallop_cutter(
    x0: float,
    x1: float,
    y_wall_edge: float,
    y_tray_side: float,
    z_floor: float,
    z_top: float,
    x_bleed_left: float = 0.0,
    x_bleed_right: float = 0.0,
    y_overshoot: float = 0.0,
    z_overshoot: float = 0.0,
    edge_strip_width: float = 0.0,
    cut_start_z: float = 0.0,
):
    bleed_left = max(0.0, x_bleed_left)
    bleed_right = max(0.0, x_bleed_right)
    x0_cut = x0 - bleed_left
    x1_cut = x1 + bleed_right
    dy = y_tray_side - y_wall_edge
    y_dir = 1.0 if dy >= 0 else -1.0
    y_tray_cut = y_tray_side + y_dir * max(0.0, y_overshoot)
    z_floor_cut = z_floor - max(0.0, z_overshoot)
    straight = _build_single_wall_side_buttress(
        x0=x0_cut,
        x1=x1_cut,
        y_wall_edge=y_wall_edge,
        y_tray_side=y_tray_cut,
        z_floor=z_floor_cut,
        z_top=z_top,
        use_arc=False,
    )
    if straight is None:
        return None

    curved = _build_single_wall_side_buttress(
        x0=x0_cut,
        x1=x1_cut,
        y_wall_edge=y_wall_edge,
        y_tray_side=y_tray_cut,
        z_floor=z_floor_cut,
        z_top=z_top,
        use_arc=True,
        arc_fallback_to_straight=False,
    )
    if curved is None:
        return None
    cutter = _coerce_single_shape(straight - curved, "wall_side_buttress_scallop_cutter")

    # Keep an uncut strip near the tray edge so support toes stay anchored to the side edge.
    keep_w = max(0.0, edge_strip_width)
    dy_total = y_tray_cut - y_wall_edge
    if keep_w > 0 and abs(dy_total) > 0.3:
        keep_w = min(keep_w, max(0.0, abs(dy_total) - 0.15))
        if keep_w > 0.01:
            if dy_total >= 0:
                keep_y0 = y_tray_cut - keep_w
                keep_y1 = y_tray_cut + 0.3
            else:
                keep_y0 = y_tray_cut - 0.3
                keep_y1 = y_tray_cut + keep_w
            keep_box = _box_min(
                (x1_cut - x0_cut) + 0.5,
                max(0.1, keep_y1 - keep_y0),
                (z_top - z_floor_cut) + 0.6,
                x0_cut - 0.25,
                keep_y0,
                z_floor_cut - 0.3,
            )
            cutter = _coerce_single_shape(cutter - keep_box, "wall_side_buttress_scallop_cutter_keep_edge")

    # Start the cut above the floor to avoid tiny toe notches at the tray edge.
    start_z = z_floor_cut + max(0.0, cut_start_z)
    if start_z < z_top - 0.2:
        cut_box = _box_min(
            (x1_cut - x0_cut) + 0.5,
            abs(y_tray_cut - y_wall_edge) + 0.8,
            (z_top - start_z) + 0.4,
            x0_cut - 0.25,
            min(y_wall_edge, y_tray_cut) - 0.4,
            start_z,
        )
        cutter = _coerce_single_shape(cutter.intersect(cut_box), "wall_side_buttress_scallop_cutter_cut_window")

    return cutter


def _build_slot_floor_scallop_strip(
    left_wall: tuple[float, float, float, float, float, str],
    right_wall: tuple[float, float, float, float, float, str],
    side: str,
    params: RibShelfParams,
    derived: Derived,
):
    left_x1 = left_wall[1]
    right_x0 = right_wall[0]
    slot_clear = right_x0 - left_x1
    if slot_clear <= 0.2:
        return None

    radius = min(max(0.0, params.slot_floor_scallop_max_radius), slot_clear * 0.5)
    if radius <= 0.15:
        return None

    # Use the outboard-most radial point of this slot fillet pair as the side-stop reference.
    # This intentionally lets inboard parts overrun and be cleanly clipped by the final tray mask.
    x_outboard = right_x0
    y_side = _tray_side_y_at_x(derived, x_outboard, side, params.wall_print_sweep_edge_inset)
    left_y0, left_y1 = left_wall[2], left_wall[3]
    right_y0, right_y1 = right_wall[2], right_wall[3]

    if side == "front":
        y_start = min(left_y1, right_y1)
    else:
        y_start = max(left_y0, right_y0)

    # Extend slightly past tray edge so final tray mask clips to a clean flush edge.
    y_dir = 1.0 if (y_side - y_start) >= 0 else -1.0
    y_side_ext = y_side + y_dir * max(0.0, params.slot_floor_scallop_edge_overrun)
    y0 = min(y_start, y_side_ext)
    y1 = max(y_start, y_side_ext)
    y_span = y1 - y0
    if y_span <= 0.2:
        return None

    y_mid = (y0 + y1) * 0.5
    cutter_len = y_span + 0.3
    z_base = params.floor_thickness
    z_center = z_base + radius

    # Two slot-local strips (one from each wall), each width == radius.
    # They naturally merge when slot_clear <= 2*radius (e.g. <= 6 mm at max radius 3 mm).
    left_strip = _box_min(
        radius,
        y_span,
        radius,
        left_x1,
        y0,
        z_base,
    )
    left_cutter = Cylinder(radius, cutter_len, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    left_cutter = left_cutter.rotate(Axis.X, 90.0).translate((left_x1 + radius, y_mid, z_center))
    left_strip = _coerce_single_shape(left_strip - left_cutter, f"slot_floor_scallop_left_{side}")

    right_strip = _box_min(
        radius,
        y_span,
        radius,
        right_x0 - radius,
        y0,
        z_base,
    )
    right_cutter = Cylinder(radius, cutter_len, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    right_cutter = right_cutter.rotate(Axis.X, 90.0).translate((right_x0 - radius, y_mid, z_center))
    right_strip = _coerce_single_shape(right_strip - right_cutter, f"slot_floor_scallop_right_{side}")

    return _coerce_single_shape(left_strip + right_strip, f"slot_floor_scallop_strip_{side}")


def _tray_side_y_at_x(derived: Derived, x_local: float, side: str, edge_inset: float = 0.0) -> float:
    # Tray perimeter on a given side is constrained by both:
    # 1) side radial line at shelf_a_start/end, and
    # 2) outer annulus arc near the outboard radius.
    angle_deg = derived.shelf_a_end if side == "back" else derived.shelf_a_start
    sign = 1.0 if angle_deg >= 0 else -1.0
    angle_abs = abs(math.radians(angle_deg))
    radius_along_axis = x_local + derived.mount_wall_radius
    inset = max(0.0, edge_inset)

    side_mag = max(0.0, radius_along_axis * math.tan(angle_abs))
    outer_r = max(0.1, derived.outer_radius - inset)
    outer_term = max(0.0, outer_r * outer_r - radius_along_axis * radius_along_axis)
    outer_mag = math.sqrt(outer_term)
    y_mag = max(0.0, min(side_mag, outer_mag) - inset)
    return sign * y_mag


def _build_edge_cleanup_band_cutter(
    derived: Derived,
    side: str,
    band_width: float,
    z0: float,
    height: float,
    outside_ratio: float,
):
    width = max(0.0, band_width)
    h = max(0.0, height)
    if width <= 1e-6 or h <= 1e-6:
        return None

    delta_deg = math.degrees(width / max(1e-6, derived.centerline_radius))
    out_deg = delta_deg * max(0.0, outside_ratio)
    if side == "front":
        a0 = derived.shelf_a_start - out_deg
        a1 = derived.shelf_a_start + delta_deg
    else:
        a0 = derived.shelf_a_end - delta_deg
        a1 = derived.shelf_a_end + out_deg

    return _build_annular_sector_prism(
        max(0.1, derived.inner_radius - 0.8),
        derived.outer_radius + 0.8,
        a0,
        a1,
        z0=z0,
        height=h,
        axis_r=derived.mount_wall_radius,
    )


def _slot_layout(params: RibShelfParams, floor_x_min: float) -> tuple[
    list[tuple[float, float]],
    list[tuple[float, float]],
    list[float],
    list[float],
    float,
]:
    count = max(1, params.slot_count)
    widths_raw = list(params.slot_widths)
    if len(widths_raw) < count:
        widths_raw = widths_raw + [widths_raw[-1] if widths_raw else 4.0] * (count - len(widths_raw))
    widths = [max(0.2, widths_raw[i]) for i in range(count)]

    # Layout lanes between inner/outer guard walls.
    # Keep lane spacing driven by widths + target pitch only; do not "fill" to tray width.
    # This lets radial_width extend tray margins without stretching lane spacing.
    available_internal = max(0.0, params.radial_width - 2.0 * params.wall_thickness)
    base_cluster = sum(widths) + max(0, count - 1) * params.wall_thickness

    desired_extras: list[float] = []
    for i in range(max(0, count - 1)):
        nominal_center_span = widths[i] * 0.5 + params.wall_thickness + widths[i + 1] * 0.5
        desired_extras.append(max(0.0, params.slot_pitch - nominal_center_span))

    available_extras = max(0.0, available_internal - base_cluster)
    desired_extras_total = sum(desired_extras)
    if count <= 1:
        extra_gaps = []
    elif available_extras <= 1e-9:
        extra_gaps = [0.0] * (count - 1)
    else:
        if desired_extras_total > 1e-9:
            scale = min(1.0, available_extras / desired_extras_total)
            extra_gaps = [gap * scale for gap in desired_extras]
        else:
            extra_gaps = [0.0] * (count - 1)

    total_cluster = base_cluster + sum(extra_gaps)
    x_cursor = floor_x_min + params.wall_thickness

    lane_bounds: list[tuple[float, float]] = []
    divider_bounds: list[tuple[float, float]] = []
    lane_centers: list[float] = []

    for i, width in enumerate(widths):
        left = x_cursor
        right = left + width
        lane_bounds.append((left, right))
        lane_centers.append((left + right) * 0.5)
        x_cursor = right
        if i < count - 1:
            d_left = x_cursor
            d_right = d_left + params.wall_thickness
            divider_bounds.append((d_left, d_right))
            x_cursor = d_right + extra_gaps[i]

    return lane_bounds, divider_bounds, lane_centers, extra_gaps, total_cluster


def derive(params: RibShelfParams, profile: CClampProfile) -> Derived:
    radius_ref_x = profile.hook_center_x if params.radius_ref_mode == "hook_center" else profile.max_profile_x
    axis_x = radius_ref_x - params.radius
    axis_shift_x = -axis_x
    mount_wall_radius = profile.max_profile_x + axis_shift_x
    pad_outer_radius = mount_wall_radius + params.pad_length

    # Keep a robust shelf-to-pad overlap region for one-piece prints.
    inner_radius = pad_outer_radius - max(params.mount_overlap, params.wall_thickness)
    outer_radius = inner_radius + params.radial_width
    centerline_radius = (inner_radius + outer_radius) * 0.5
    shelf_angle_deg = math.degrees(params.arc_length / max(1e-6, centerline_radius))
    sweep_angle_eff = shelf_angle_deg + max(0.0, params.sweep_support_margin_deg)
    sweep_sign = 1.0 if params.sweep_direction >= 0 else -1.0

    # Keep local shelf symmetric (prevents clipping of ±Y linear wall geometry),
    # then rotate into the clamp's 0..sweep span so tray and clamp sides align.
    attach_angle = sweep_sign * sweep_angle_eff * 0.5
    shelf_a_start = -sweep_angle_eff * 0.5
    shelf_a_end = sweep_angle_eff * 0.5

    holder_top_z = profile.max_profile_y + params.pad_offset_y + params.shelf_top_offset - params.axis_z
    holder_profile_y_sweep = holder_top_z

    floor_x_min = -mount_wall_radius + inner_radius
    floor_y_span = max(params.arc_length + params.wall_thickness * 1.5, params.slot_depth + params.wall_thickness * 6.0)
    slot_y_front = -params.slot_depth * 0.5
    slot_y_back = slot_y_front + params.slot_depth

    lane_bounds, divider_bounds, lane_centers, lane_gaps_extra, total_cluster = _slot_layout(params, floor_x_min)

    wall_count = max(2, params.slot_count + 1)
    wall_h0 = max(6.0, params.inner_wall_height)
    wall_h1 = max(wall_h0, params.outer_wall_height)
    wall_heights = [
        wall_h0 + (wall_h1 - wall_h0) * (i / (wall_count - 1))
        for i in range(wall_count)
    ]
    wall_l0 = max(params.wall_thickness * 2.0, min(params.slot_depth, params.inner_wall_length))
    wall_l1 = max(wall_l0, min(params.slot_depth, params.outer_wall_length))
    wall_lengths = [
        wall_l0 + (wall_l1 - wall_l0) * (i / (wall_count - 1))
        for i in range(wall_count)
    ]

    mask_z0 = -1.0
    mask_height = params.floor_thickness + wall_h1 + 4.0

    return Derived(
        radius_ref_x=radius_ref_x,
        axis_x=axis_x,
        axis_shift_x=axis_shift_x,
        mount_wall_radius=mount_wall_radius,
        pad_outer_radius=pad_outer_radius,
        inner_radius=inner_radius,
        outer_radius=outer_radius,
        centerline_radius=centerline_radius,
        sweep_angle_eff=sweep_angle_eff,
        sweep_sign=sweep_sign,
        shelf_angle_deg=shelf_angle_deg,
        attach_angle=attach_angle,
        shelf_a_start=shelf_a_start,
        shelf_a_end=shelf_a_end,
        holder_top_z=holder_top_z,
        holder_profile_y_sweep=holder_profile_y_sweep,
        floor_x_min=floor_x_min,
        floor_y_span=floor_y_span,
        slot_y_front=slot_y_front,
        slot_y_back=slot_y_back,
        lane_bounds=lane_bounds,
        divider_bounds=divider_bounds,
        lane_centers=lane_centers,
        lane_gaps_extra=lane_gaps_extra,
        total_lane_cluster_width=total_cluster,
        wall_heights=wall_heights,
        wall_lengths=wall_lengths,
        mask_z0=mask_z0,
        mask_height=mask_height,
        intended_mount_clock_position=params.mount_clock_position,
    )


def build_clamp_pad_sweep(params: RibShelfParams, profile: CClampProfile, derived: Derived):
    parts = []
    x_shift = derived.axis_shift_x
    z_shift = -params.axis_z

    if params.show_clamp:
        clamp_profile_xz = [(x + x_shift, y + z_shift) for (x, y) in profile.points]
        parts.append(_revolve_closed_profile(clamp_profile_xz, derived.sweep_angle_eff))

    if params.show_pad:
        x0 = profile.max_profile_x - params.pad_overlap + x_shift
        z0 = profile.max_profile_y - params.pad_thickness + params.pad_offset_y + z_shift
        x1 = x0 + params.pad_length + params.pad_overlap
        z1 = z0 + params.pad_thickness
        pad_profile_xz = [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
        parts.append(_revolve_closed_profile(pad_profile_xz, derived.sweep_angle_eff))

    if not parts:
        return None

    merged = parts[0]
    for piece in parts[1:]:
        merged = merged + piece
    if derived.sweep_sign < 0:
        merged = merged.rotate(Axis.Z, -derived.sweep_angle_eff)
    return merged


def build_shelf_linear(params: RibShelfParams, derived: Derived):
    # Radial tray floor: build directly as annular-sector prism.
    floor = _build_annular_sector_prism(
        max(0.1, derived.inner_radius),
        derived.outer_radius,
        derived.shelf_a_start,
        derived.shelf_a_end,
        z0=0.0,
        height=params.floor_thickness,
        axis_r=derived.mount_wall_radius,
    )
    if floor is None:
        raise ValueError("Invalid radial floor dimensions.")

    # Full-height boundary walls so the first and last slot are fully usable.
    wall_specs: list[tuple[float, float, float, float, float, str]] = []

    inner_len = derived.wall_lengths[0]
    inner_y0 = -inner_len * 0.5
    inner_x0 = (
        derived.lane_bounds[0][0] - params.wall_thickness
        if derived.lane_bounds
        else derived.floor_x_min
    )
    inner_guard = _box_min(
        params.wall_thickness,
        inner_len,
        derived.wall_heights[0],
        inner_x0,
        inner_y0,
        params.floor_thickness,
    )
    wall_specs.append(
        (
            inner_x0,
            inner_x0 + params.wall_thickness,
            inner_y0,
            inner_y0 + inner_len,
            derived.wall_heights[0],
            "inner_guard",
        )
    )
    outer_len = derived.wall_lengths[-1]
    outer_x0 = (
        derived.lane_bounds[-1][1]
        if derived.lane_bounds
        else (derived.floor_x_min + params.radial_width - params.wall_thickness)
    )
    outer_y0 = -outer_len * 0.5
    outer_guard = _box_min(
        params.wall_thickness,
        outer_len,
        derived.wall_heights[-1],
        outer_x0,
        outer_y0,
        params.floor_thickness,
    )
    wall_specs.append(
        (
            outer_x0,
            outer_x0 + params.wall_thickness,
            outer_y0,
            outer_y0 + outer_len,
            derived.wall_heights[-1],
            "outer_guard",
        )
    )

    shelf = floor + inner_guard + outer_guard
    for i, (d0, d1) in enumerate(derived.divider_bounds):
        wall_h = derived.wall_heights[min(i + 1, len(derived.wall_heights) - 1)]
        wall_len = derived.wall_lengths[min(i + 1, len(derived.wall_lengths) - 1)]
        wall_y0 = -wall_len * 0.5
        shelf = shelf + _box_min(
            d1 - d0,
            wall_len,
            wall_h,
            d0,
            wall_y0,
            params.floor_thickness,
        )
        wall_specs.append((d0, d1, wall_y0, wall_y0 + wall_len, wall_h, "divider"))

    walls_sorted = sorted(wall_specs, key=lambda w: w[0])

    def _slot_radius_from_clear(slot_clear: float) -> float:
        return min(max(0.0, params.slot_floor_scallop_max_radius), max(0.0, slot_clear) * 0.5)

    cut_margin = max(0.0, params.wall_print_scallop_cut_x_bleed)
    wall_cut_bleeds: dict[tuple[float, float, float, float], tuple[float, float]] = {}
    for idx, (wx0, wx1, wy0, wy1, _, _) in enumerate(walls_sorted):
        left_slot_clear = 0.0 if idx == 0 else (wx0 - walls_sorted[idx - 1][1])
        right_slot_clear = 0.0 if idx == len(walls_sorted) - 1 else (walls_sorted[idx + 1][0] - wx1)
        left_bleed = _slot_radius_from_clear(left_slot_clear) + cut_margin
        right_bleed = _slot_radius_from_clear(right_slot_clear) + cut_margin
        wall_cut_bleeds[(wx0, wx1, wy0, wy1)] = (left_bleed, right_bleed)

    buttress_scallop_cutters = []
    if params.show_wall_print_sweeps:
        z_floor = params.floor_thickness
        for x0, x1, y0, y1, wall_h, kind in walls_sorted:
            if wall_h <= 0.6:
                continue
            x_bleed_left, x_bleed_right = wall_cut_bleeds.get((x0, x1, y0, y1), (cut_margin, cut_margin))
            # Side-stop target is based on outboard-most radial extent of the geometry.
            # With circle-cut enabled, use cutter outboard extent; otherwise use wall outboard face.
            x_outboard = x1 + (x_bleed_right if params.wall_print_sweep_circle_cut else 0.0)
            y_front_target = _tray_side_y_at_x(derived, x_outboard, "front", params.wall_print_sweep_edge_inset)
            y_back_target = _tray_side_y_at_x(derived, x_outboard, "back", params.wall_print_sweep_edge_inset)
            y_overshoot_eff = max(params.wall_print_scallop_cut_y_overshoot, x_bleed_left, x_bleed_right)
            z_overshoot_eff = max(params.wall_print_scallop_cut_z_overshoot, 0.45 * max(x_bleed_left, x_bleed_right))

            if params.wall_print_sweep_render_front_side:
                buttress_front = _build_single_wall_side_buttress(
                    x0=x0,
                    x1=x1,
                    y_wall_edge=y0,
                    y_tray_side=y_front_target,
                    z_floor=z_floor,
                    z_top=z_floor + wall_h,
                    use_arc=False,
                )
                if buttress_front is not None:
                    shelf = shelf + buttress_front
                if params.wall_print_sweep_circle_cut:
                    cutter_front = _build_wall_side_buttress_scallop_cutter(
                        x0=x0,
                        x1=x1,
                        y_wall_edge=y0,
                        y_tray_side=y_front_target,
                        z_floor=z_floor,
                        z_top=z_floor + wall_h,
                        x_bleed_left=x_bleed_left,
                        x_bleed_right=x_bleed_right,
                        y_overshoot=y_overshoot_eff,
                        z_overshoot=z_overshoot_eff,
                        edge_strip_width=params.wall_print_scallop_edge_strip_width,
                        cut_start_z=params.wall_print_scallop_cut_start_z,
                    )
                    if cutter_front is not None:
                        buttress_scallop_cutters.append(cutter_front)

            if params.wall_print_sweep_render_back_side:
                buttress_back = _build_single_wall_side_buttress(
                    x0=x0,
                    x1=x1,
                    y_wall_edge=y1,
                    y_tray_side=y_back_target,
                    z_floor=z_floor,
                    z_top=z_floor + wall_h,
                    use_arc=False,
                )
                if buttress_back is not None:
                    shelf = shelf + buttress_back
                if params.wall_print_sweep_circle_cut:
                    cutter_back = _build_wall_side_buttress_scallop_cutter(
                        x0=x0,
                        x1=x1,
                        y_wall_edge=y1,
                        y_tray_side=y_back_target,
                        z_floor=z_floor,
                        z_top=z_floor + wall_h,
                        x_bleed_left=x_bleed_left,
                        x_bleed_right=x_bleed_right,
                        y_overshoot=y_overshoot_eff,
                        z_overshoot=z_overshoot_eff,
                        edge_strip_width=params.wall_print_scallop_edge_strip_width,
                        cut_start_z=params.wall_print_scallop_cut_start_z,
                    )
                    if cutter_back is not None:
                        buttress_scallop_cutters.append(cutter_back)

    # Slot-driven wall/floor scallops:
    # radius = min(slot_floor_scallop_max_radius, 0.5 * slot_clearance)
    support_sides = []
    if params.wall_print_sweep_render_front_side:
        support_sides.append("front")
    if params.wall_print_sweep_render_back_side:
        support_sides.append("back")
    if params.slot_floor_scallop_max_radius > 0 and support_sides:
        for side in support_sides:
            for idx in range(len(walls_sorted) - 1):
                strip = _build_slot_floor_scallop_strip(
                    left_wall=walls_sorted[idx],
                    right_wall=walls_sorted[idx + 1],
                    side=side,
                    params=params,
                    derived=derived,
                )
                if strip is not None:
                    shelf = shelf + strip

    # Apply support scallop cuts after slot-floor fillets so the buttress cut profiles carry through.
    if params.wall_print_sweep_circle_cut and buttress_scallop_cutters:
        for idx, cutter in enumerate(buttress_scallop_cutters):
            shelf = _coerce_single_shape(shelf - cutter, f"shelf_after_buttress_scallop_{idx}")

    # Soften exposed vertical corners.
    shelf = _safe_fillet(
        shelf,
        list(shelf.edges().filter_by(Axis.Z)),
        params.edge_fillet_radius,
        "shelf_vertical_edges",
    )

    shelf = _coerce_single_shape(shelf, "shelf_pre_cleanup")

    # Build final tray-edge mask once; apply as the final operation after all local cleanup cuts.
    mask = _build_annular_sector_prism(
        max(0.1, derived.inner_radius - 0.4),
        derived.outer_radius + 0.4,
        derived.shelf_a_start,
        derived.shelf_a_end,
        z0=derived.mask_z0,
        height=derived.mask_height,
        axis_r=derived.mount_wall_radius,
    )

    # Final edge cleanup band cut to remove tiny residual tabs at tray side boundaries.
    cleanup_band_sides = []
    if params.wall_print_sweep_render_front_side:
        cleanup_band_sides.append("front")
    if params.wall_print_sweep_render_back_side:
        cleanup_band_sides.append("back")
    cleanup_band_width = max(0.0, params.slot_edge_cleanup_band_width)
    cleanup_band_height = max(0.0, params.slot_edge_cleanup_band_height)
    cleanup_band_drop = max(0.0, params.slot_edge_cleanup_band_z_drop)
    if cleanup_band_width > 0 and cleanup_band_height > 0 and cleanup_band_sides:
        cleanup_z0 = params.floor_thickness - cleanup_band_drop
        cleanup_h = cleanup_band_height + cleanup_band_drop
        for side in cleanup_band_sides:
            cleanup_cutter = _build_edge_cleanup_band_cutter(
                derived=derived,
                side=side,
                band_width=cleanup_band_width,
                z0=cleanup_z0,
                height=cleanup_h,
                outside_ratio=params.slot_edge_cleanup_band_outside_ratio,
            )
            if cleanup_cutter is not None:
                shelf = _coerce_single_shape(shelf - cleanup_cutter, f"shelf_edge_cleanup_band_{side}")

    if mask is not None:
        shelf = _coerce_single_shape(shelf.intersect(mask), "shelf_final_mask")
    shelf = _coerce_single_shape(shelf, "shelf_masked")
    return _prune_tiny_detached_solids(shelf, params.fragment_prune_max_volume_mm3, "shelf")


def _build_mount_underside_blend(params: RibShelfParams, derived: Derived, shelf_bottom_z: float):
    blend_r = max(0.0, params.mount_underside_fillet_radius)
    if blend_r <= 0:
        return None

    # Keep blend inside the overlap region so it supports the joint without overgrowth.
    blend_r = min(blend_r, max(0.2, params.mount_overlap - 0.35))
    if blend_r <= 0.15:
        return None

    with BuildPart() as torus:
        with BuildSketch(Plane.XZ):
            with Locations((derived.inner_radius, shelf_bottom_z)):
                Circle(blend_r)
        revolve(axis=Axis.Z, revolution_arc=derived.sweep_angle_eff)
    blend = torus.part

    radial_lower_mask = _build_annular_sector_prism(
        max(0.1, derived.inner_radius - 0.02),
        derived.inner_radius + blend_r + 0.15,
        0.0,
        derived.sweep_angle_eff,
        z0=shelf_bottom_z - blend_r - 0.2,
        height=blend_r + 0.25,
        axis_r=0.0,
    )
    if radial_lower_mask is not None:
        blend = blend.intersect(radial_lower_mask)
    return _coerce_single_shape(blend, "mount_underside_blend")


def _rotate_about_y_at_x(part, angle_deg: float, pivot_x: float):
    if abs(angle_deg) <= 1e-9:
        return part
    return part.translate((-pivot_x, 0.0, 0.0)).rotate(Axis.Y, angle_deg).translate((pivot_x, 0.0, 0.0))


def build_assembly(params: RibShelfParams, profile: CClampProfile):
    derived = derive(params, profile)
    parts = []
    clamp_pad = build_clamp_pad_sweep(params, profile, derived)
    if clamp_pad is not None:
        parts.append(clamp_pad)

    if params.show_shelf:
        shelf = build_shelf_linear(params, derived)
        shelf = _rotate_about_y_at_x(shelf, -params.tilt_deg, derived.inner_radius - derived.mount_wall_radius)
        z_embed = min(params.floor_thickness * 0.8, max(params.pad_overlap, params.mount_overlap * 0.35))
        # Transform order matters:
        # 1) shift shelf so its radial-center frame matches clamp center (origin),
        # 2) then apply sweep-angle placement around that shared origin.
        shelf = shelf.translate((derived.mount_wall_radius, 0.0, derived.holder_profile_y_sweep - z_embed))
        shelf = shelf.rotate(Axis.Z, derived.attach_angle)
        parts.append(shelf)

    if not parts:
        raise ValueError("All geometry sections are disabled; nothing to build.")

    model = parts[0]
    for piece in parts[1:]:
        model = model + piece

    # Explicit constructive underside blend where shelf meets clamp/pad.
    if params.show_shelf and params.show_clamp:
        z_embed = min(params.floor_thickness * 0.8, max(params.pad_overlap, params.mount_overlap * 0.35))
        shelf_bottom_z = derived.holder_profile_y_sweep - z_embed
        mount_blend = _build_mount_underside_blend(params, derived, shelf_bottom_z)
        if mount_blend is not None:
            model = model + mount_blend
    model = _coerce_single_shape(model, "assembly")
    model = _prune_tiny_detached_solids(model, params.fragment_prune_max_volume_mm3, "assembly")
    return model, derived


def print_checks(params: RibShelfParams, derived: Derived) -> None:
    print(f"INFO: intended_mount_clock_position = {derived.intended_mount_clock_position}:00 (user at 6:00)")
    print(f"INFO: material_profile = {params.material} (v2 target: PETG)")
    print(f"INFO: slot_count = {params.slot_count}, lane_cluster_width = {derived.total_lane_cluster_width:.2f} mm")
    print(
        f"INFO: shelf arc = {params.arc_length:.2f} mm, radial width = {params.radial_width:.2f} mm, "
        f"slot depth = {params.slot_depth:.2f} mm"
    )
    print(
        f"INFO: sweep_angle_eff = {derived.sweep_angle_eff:.2f} deg (tray-driven), "
        f"shelf_span = {derived.shelf_angle_deg:.2f} deg, mount_overlap = {params.mount_overlap:.2f} mm"
    )
    clamp_midline = derived.sweep_sign * derived.sweep_angle_eff * 0.5
    print(
        f"INFO: sweep_midline_alignment_deg clamp={clamp_midline:.2f}, "
        f"holders={derived.attach_angle:.2f}"
    )
    print(
        f"INFO: wall_height_gradient_inner_to_outer = "
        f"{derived.wall_heights[0]:.1f} -> {derived.wall_heights[-1]:.1f} mm"
    )
    print(
        f"INFO: wall_length_gradient_inner_to_outer = "
        f"{derived.wall_lengths[0]:.1f} -> {derived.wall_lengths[-1]:.1f} mm"
    )
    print(
        f"INFO: wall_root_fillet_mode = slot_scallop_strip, "
        f"legacy_wall_floor_radius = {params.wall_floor_fillet_radius:.2f} mm, "
        f"slot_scallop_max_radius = {params.slot_floor_scallop_max_radius:.2f} mm, "
        f"slot_scallop_width_extra = {params.slot_floor_scallop_width_extra:.2f} mm (unused in current mode), "
        f"slot_scallop_edge_overrun = {params.slot_floor_scallop_edge_overrun:.2f} mm, "
        f"edge_cleanup_band = w{params.slot_edge_cleanup_band_width:.2f}/h{params.slot_edge_cleanup_band_height:.2f}/drop{params.slot_edge_cleanup_band_z_drop:.2f} mm, "
        f"outside_ratio = {params.slot_edge_cleanup_band_outside_ratio:.2f}"
    )
    print(
        f"INFO: mount_underside_blend_mode = constructive_swept, radius = {max(0.0, min(params.mount_underside_fillet_radius, max(0.2, params.mount_overlap - 0.35))):.2f} mm"
    )
    print(
        f"INFO: wall_print_sweeps = {params.show_wall_print_sweeps}, "
        f"one_per_wall = True, thickness = wall_thickness ({params.wall_thickness:.2f} mm), "
        f"circle_cut = {params.wall_print_sweep_circle_cut}, "
        f"edge_target = outboard_radial_point, "
        f"scallop_cut_x_bleed = auto_from_adjacent_slot_radii + {params.wall_print_scallop_cut_x_bleed:.2f} mm margin, "
        f"scallop_cut_y_overshoot = max({params.wall_print_scallop_cut_y_overshoot:.2f}, local_bleed) mm, "
        f"scallop_cut_z_overshoot = max({params.wall_print_scallop_cut_z_overshoot:.2f}, 0.45*local_bleed) mm, "
        f"scallop_edge_strip_width = {params.wall_print_scallop_edge_strip_width:.2f} mm, "
        f"scallop_cut_start_z = {params.wall_print_scallop_cut_start_z:.2f} mm, "
        f"edge_inset = {params.wall_print_sweep_edge_inset:.2f} mm, "
        f"front_side = {params.wall_print_sweep_render_front_side}, "
        f"back_side = {params.wall_print_sweep_render_back_side}"
    )
    lane_widths = [right - left for (left, right) in derived.lane_bounds]
    lane_widths_text = ", ".join(f"{width:.2f}" for width in lane_widths)
    print(f"INFO: lane_clear_widths_mm = [{lane_widths_text}]")
    scallop_radii = [min(max(0.0, params.slot_floor_scallop_max_radius), width * 0.5) for width in lane_widths]
    scallop_radii_text = ", ".join(f"{radius:.2f}" for radius in scallop_radii)
    print(f"INFO: slot_floor_scallop_radii_mm = [{scallop_radii_text}]")
    if len(derived.lane_centers) > 1:
        center_pitches = [
            derived.lane_centers[i + 1] - derived.lane_centers[i]
            for i in range(len(derived.lane_centers) - 1)
        ]
        pitch_text = ", ".join(f"{pitch:.2f}" for pitch in center_pitches)
        print(f"INFO: lane_center_pitches_mm = [{pitch_text}]")

    nozzle_min_wall = params.min_wall_for_nozzle_multiplier * NOZZLE_DIAMETER_MM
    if params.wall_thickness < nozzle_min_wall:
        print(
            "WARNING: wall_thickness may be too thin for a 0.4 mm nozzle "
            f"({params.wall_thickness:.2f} < {nozzle_min_wall:.2f} mm)."
        )
    if params.floor_thickness < params.min_floor_recommended:
        print("WARNING: floor_thickness is thin for repeated wet use.")
    if params.inner_wall_length > params.slot_depth or params.outer_wall_length > params.slot_depth:
        print(
            "WARNING: wall length targets exceed slot depth and are being clipped "
            f"to {params.slot_depth:.2f} mm."
        )

    if len(params.slot_widths) != params.slot_count:
        print("WARNING: slot_count and PRIMARY_SLOT_WIDTHS_MM length mismatch; widths are being normalized.")

    # Guardrail: slot overlap / invalid lane ordering.
    for i in range(len(derived.lane_bounds) - 1):
        right_i = derived.lane_bounds[i][1]
        left_next = derived.lane_bounds[i + 1][0]
        if right_i >= left_next:
            print(f"WARNING: slot overlap detected between lanes {i + 1} and {i + 2}.")

    # Guardrail: impossible pitch relative to lane widths/walls.
    widths = list(params.slot_widths)[: params.slot_count]
    if len(widths) < params.slot_count and widths:
        widths.extend([widths[-1]] * (params.slot_count - len(widths)))
    for i in range(max(0, params.slot_count - 1)):
        if i + 1 >= len(widths):
            break
        min_center_span = widths[i] * 0.5 + params.wall_thickness + widths[i + 1] * 0.5
        if params.slot_pitch + 1e-6 < min_center_span:
            print(
                "WARNING: requested slot_pitch is impossible for current adjacent lane widths/wall thickness "
                f"(pair {i + 1}-{i + 2}, needs >= {min_center_span:.2f} mm)."
            )
    if len(derived.lane_centers) > 1:
        center_pitches = [
            derived.lane_centers[i + 1] - derived.lane_centers[i]
            for i in range(len(derived.lane_centers) - 1)
        ]
        largest_pitch_delta = max(abs(pitch - params.slot_pitch) for pitch in center_pitches)
        if largest_pitch_delta > 0.8:
            print(
                "INFO: actual lane center pitches are width-driven and differ from requested slot_pitch by up to "
                f"{largest_pitch_delta:.2f} mm."
            )

    if derived.total_lane_cluster_width > params.radial_width + 1e-6:
        print("WARNING: slot layout exceeds radial width; reduce widths, pitch, or wall thickness.")

    # Guardrail: impossible pitch/count against arc length (access staging sanity check).
    pitch_span = max(0, params.slot_count - 1) * params.slot_pitch
    if pitch_span > params.arc_length + 1e-6:
        print("WARNING: slot count/pitch exceeds available arc length envelope.")

    # Guardrail: trapped water pockets.
    if params.slot_depth > params.arc_length - params.wall_thickness * 2.0:
        print("WARNING: slot_depth is near full shelf span; rinse-out access may be reduced.")
    if derived.slot_y_back > params.arc_length * 0.5:
        print("WARNING: slot depth pushes beyond shelf span; likely invalid/wet pocket geometry.")

    if params.radial_width > params.max_projection:
        print("WARNING: projection exceeds max_projection guideline.")
    if derived.shelf_angle_deg > derived.sweep_angle_eff + 0.1:
        print(
            "WARNING: shelf arc span exceeds effective clamp sweep span; outboard ends are cantilevered "
            f"({derived.shelf_angle_deg:.2f} deg > {derived.sweep_angle_eff:.2f} deg)."
        )


def print_geometry_summary(model) -> None:
    model = _coerce_single_shape(model, "summary_model")
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
    parser = argparse.ArgumentParser(description="build123d rib shelf vertical v1.")
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
    params = RibShelfParams()
    profile = load_c_clamp_profile()
    profile = stretch_profile_from_back_wall_mid(profile, params.clamp_back_wall_stretch)

    model, derived = build_assembly(params, profile)
    print_checks(params, derived)
    print_geometry_summary(model)

    if run.preview:
        preview_part(model)
        if not run.export:
            print("Preview-only mode: STL export skipped.")
            return 0

    out_path = run.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    export_stl(model, str(out_path), tolerance=0.0005, angular_tolerance=0.03)
    print(f"Exported: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
