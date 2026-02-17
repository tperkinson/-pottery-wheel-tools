// throwing_water_holder (v1)
// Native radial basin: one side starts at 0 deg, opposite side at +span deg.

$fn = 96;//96;
include <../../../core_mount_system/c_clamp/v1/c_clamp_profile_topref_v1.scad>;

// -------------------------------
// Quick Tuning
// -------------------------------
render_holder_only = true;
holder_only_side_print = true;

show_clamp = true;
show_pad = false;
show_holder = true;

radius = 222.25;
radius_ref_mode = "hook_center";
axis_z = 0;

sweep_angle = 24;
pad_length = 8;
pad_thickness = 4;
pad_overlap = 1.0;
pad_offset_y = 0;

holder_top_offset = 16;
holder_tilt_deg = 0;
holder_angle_offset = 0;           // side-start angle on sweep
holder_radial_location_on_pad = 0;
shared_wall_overlap = 1.5;

// Side-wall definition: side 1 starts at 0 deg
match_side_walls_to_sweep = true;
side_start_deg = 0;
side_span_manual_deg = 0; // <=0 means derive from arc_length
side_wall_sweep_margin_deg = 0;

// Basin dimensions
target_volume_ml = 946;
volume_headroom_ml = 120;
arc_length = 102;
radial_width = 135;
depth = 72;
back_wall_height = depth;
front_wall_height = depth; // keep top flat by default
wall_thickness = 4.8;
floor_thickness = 4.5;

// Rounding (intentionally large / organic)
plan_corner_round_radius = 8;       // rounds side-wall intersections in plan
interior_floor_blend_radius = 4.0;  // rounds side-wall/floor intersections
front_rim_round_radius = 0;
back_rim_round_radius = 0;
side_top_round_radius = 0;
front_side_corner_round_radius = 0;

// Build envelope
max_projection = 127;
ender3_v3_bed_x = 220;
ender3_v3_bed_y = 220;

// -------------------------------
// Derived
// -------------------------------
radius_ref_x = (radius_ref_mode == "hook_center") ? hook_center_x : max_profile_x;
axis_x = radius_ref_x - radius;
axis_shift_x = max(0, axis_x - min_profile_x + 0.1);

holder_origin_x = max_profile_x + holder_radial_location_on_pad;
holder_profile_y_2d = max_profile_y + holder_top_offset;
holder_profile_y_sweep = holder_profile_y_2d - axis_z;
holder_r = axis_shift_x + (holder_origin_x - axis_x);
attach_angle = holder_angle_offset;

side_span_from_arc_length_deg = (holder_r > 0) ? (arc_length / holder_r) * 180 / PI : 0;
side_span_base_deg =
    (side_span_manual_deg > 0)
    ? side_span_manual_deg
    : side_span_from_arc_length_deg;
side_span_deg =
    (match_side_walls_to_sweep ? sweep_angle : side_span_base_deg)
    + side_wall_sweep_margin_deg;
a_start = match_side_walls_to_sweep ? 0 : side_start_deg;
a_end = a_start + side_span_deg;

r_front_outer = holder_r - shared_wall_overlap;
r_back_outer = r_front_outer + radial_width;
r_front_inner = r_front_outer + wall_thickness;
r_back_inner = r_back_outer - wall_thickness;
r_mid_inner = (r_front_inner + r_back_inner) / 2;
side_wall_angle_thickness_deg = (r_mid_inner > 0) ? (wall_thickness / r_mid_inner) * 180 / PI : 0;
a_inner_start = a_start + side_wall_angle_thickness_deg;
a_inner_end = a_end - side_wall_angle_thickness_deg;
floor_blend_radius = min(
    interior_floor_blend_radius,
    max(0.5, wall_thickness - 0.4),
    (r_back_inner - r_front_inner) / 4,
    (back_wall_height - floor_thickness) / 3
);
floor_blend_angle_pad = (r_mid_inner > 0) ? (floor_blend_radius / r_mid_inner) * 180 / PI : 0;

front_wall_height_eff = min(back_wall_height - 0.1, max(floor_thickness + 1, front_wall_height));
inner_height_fill = max(0, front_wall_height_eff - floor_thickness);
inner_height_max = max(0, back_wall_height - floor_thickness);
max_safe_top_round = max(0, wall_thickness * 0.55);

angle_rad = max(0, (a_inner_end - a_inner_start) * PI / 180);
inner_plan_area_mm2 =
    (r_back_inner > r_front_inner && angle_rad > 0)
    ? 0.5 * angle_rad * (r_back_inner * r_back_inner - r_front_inner * r_front_inner)
    : 0;

fill_volume_ml_est = inner_plan_area_mm2 * inner_height_fill / 1000;
max_volume_ml_est = inner_plan_area_mm2 * inner_height_max / 1000;
back_arc_length = r_back_outer * angle_rad;

pad_outer_local_x = pad_length - holder_radial_location_on_pad;
projection_from_pad_outer = (r_back_outer - holder_r) - pad_outer_local_x;

holder_footprint_x = radial_width;
holder_footprint_y = back_arc_length;

echo(str("INFO: fill-line volume estimate (ml) = ", fill_volume_ml_est));
echo(str("INFO: max volume estimate (ml) = ", max_volume_ml_est));
echo(str("INFO: side angles (deg) = [", a_start, ", ", a_end, "]"));

if (wall_thickness < 3.0)
    echo("WARNING: wall_thickness < 3.0 mm may be weak.");
if (floor_thickness < 3.8)
    echo("WARNING: floor_thickness < 3.8 mm may be weak.");
if (r_front_inner <= 0 || r_back_inner <= r_front_inner)
    echo("WARNING: invalid annular basin radii.");
if (a_end <= a_start)
    echo("WARNING: invalid side wall angles.");
if (a_inner_end <= a_inner_start)
    echo("WARNING: side-wall thickness too large for current angular span.");
if (front_wall_height_eff <= floor_thickness)
    echo("WARNING: front wall height must exceed floor thickness.");
if (projection_from_pad_outer > max_projection)
    echo("WARNING: projection exceeds max_projection.");
if (fill_volume_ml_est < target_volume_ml)
    echo("WARNING: fill-line volume below target_volume_ml.");
if (max_volume_ml_est < target_volume_ml + volume_headroom_ml)
    echo("WARNING: max volume below target_volume_ml + volume_headroom_ml.");
if (match_side_walls_to_sweep && abs(side_start_deg) > 0.01)
    echo("WARNING: side_start_deg != 0 while sweep-match is enabled.");
if (match_side_walls_to_sweep && abs(side_span_from_arc_length_deg - sweep_angle) > 3.0)
    echo("WARNING: arc_length-implied angle differs from sweep_angle by >3 deg.");
if (a_end > sweep_angle + 0.01)
    echo("WARNING: side-end exceeds sweep angle; holder may extend beyond clamp sweep.");
if (plan_corner_round_radius > (radial_width / 2))
    echo("WARNING: plan_corner_round_radius too large for radial_width.");
if (front_rim_round_radius > front_wall_height_eff - floor_thickness)
    echo("WARNING: front_rim_round_radius too large for front wall.");
if (back_rim_round_radius > back_wall_height - floor_thickness)
    echo("WARNING: back_rim_round_radius too large for back wall.");
if (side_top_round_radius > (back_wall_height - floor_thickness))
    echo("WARNING: side_top_round_radius too large for side wall height.");
if (front_side_corner_round_radius > (front_wall_height_eff - floor_thickness))
    echo("WARNING: front_side_corner_round_radius too large for front corners.");
if (front_rim_round_radius > max_safe_top_round)
    echo("WARNING: front_rim_round_radius exceeds wall-safe limit and will be capped.");
if (back_rim_round_radius > max_safe_top_round)
    echo("WARNING: back_rim_round_radius exceeds wall-safe limit and will be capped.");
if (side_top_round_radius > max_safe_top_round)
    echo("WARNING: side_top_round_radius exceeds wall-safe limit and will be capped.");
if (front_side_corner_round_radius > max_safe_top_round)
    echo("WARNING: front_side_corner_round_radius exceeds wall-safe limit and will be capped.");
if (holder_footprint_x > ender3_v3_bed_x || holder_footprint_y > ender3_v3_bed_y)
    echo("WARNING: holder-only footprint likely exceeds Ender 3 V3 bed (220x220 mm).");

// -------------------------------
// Helpers
// -------------------------------
function arc_pt(r, a_deg, cx = 0) = [cx + r * cos(a_deg), r * sin(a_deg)];
function arc_pts(r, a0_deg, a1_deg, n, cx = 0) =
    [for (i = [0 : n]) arc_pt(r, a0_deg + (a1_deg - a0_deg) * i / n, cx)];
function seg_count_for_span(a0_deg, a1_deg) = max(24, floor($fn / 2), ceil(abs(a1_deg - a0_deg) / 1.5));
function smoothstep01(t) = t <= 0 ? 0 : (t >= 1 ? 1 : t * t * (3 - 2 * t));

module annular_wedge_raw_2d(r_in, r_out, a0_deg, a1_deg, cx = 0) {
    if (r_out > r_in && a1_deg > a0_deg) {
        n = seg_count_for_span(a0_deg, a1_deg);
        polygon(points = concat(
            arc_pts(r_out, a0_deg, a1_deg, n, cx),
            arc_pts(r_in, a1_deg, a0_deg, n, cx)
        ));
    }
}

module annular_wedge_2d(r_in, r_out, a0_deg, a1_deg, cx = 0) {
    rr = max(0, plan_corner_round_radius);
    if (rr > 0) {
        offset(r = rr)
            offset(delta = -rr)
                annular_wedge_raw_2d(r_in, r_out, a0_deg, a1_deg, cx);
    } else {
        annular_wedge_raw_2d(r_in, r_out, a0_deg, a1_deg, cx);
    }
}

// -------------------------------
// Clamp / Pad (swept)
// -------------------------------
module clamp_profile() {
    polygon(points = profile_points);
}

module pad_profile() {
    x0 = max_profile_x - pad_overlap;
    y0 = max_profile_y - pad_thickness + pad_offset_y;
    translate([x0, y0])
        square([pad_length + pad_overlap, pad_thickness], center = false);
}

module clamp_pad_profile() {
    union() {
        if (show_clamp) clamp_profile();
        if (show_pad) pad_profile();
    }
}

module clamp_pad_sweep() {
    rotate([90, 0, 0])
        rotate_extrude(angle = sweep_angle)
            translate([axis_shift_x, 0])
                translate([-axis_x, -axis_z])
                    clamp_pad_profile();
}

module attachment_frame(angle_deg, radial_r, profile_y, tangent = 0) {
    rotate([90, 0, 0])
        rotate([0, 0, angle_deg])
            translate([radial_r, tangent, profile_y])
                children();
}

// -------------------------------
// Holder Geometry (native radial)
// -------------------------------
module interior_floor_blend_subtractor_linear() {
    rr = floor_blend_radius;

    if (rr > 0.2 && (a_inner_end - a_inner_start) > (2 * floor_blend_angle_pad + 0.5)) {
        hull() {
            translate([0, 0, floor_thickness - 0.05])
                linear_extrude(height = 0.05)
                    annular_wedge_2d(
                        r_front_inner + rr,
                        r_back_inner - rr,
                        a_inner_start + floor_blend_angle_pad,
                        a_inner_end - floor_blend_angle_pad,
                        -holder_r
                    );

            translate([0, 0, floor_thickness + rr])
                linear_extrude(height = 0.05)
                    annular_wedge_2d(
                        r_front_inner,
                        r_back_inner,
                        a_inner_start,
                        a_inner_end,
                        -holder_r
                    );
        }
    }
}

module side_floor_edge_fillet_linear(side_angle_deg, side_sign, r_min, r_max, z_base) {
    rr = floor_blend_radius;
    run_len = max(0.1, (r_max - r_min) + 2 * rr);
    r_mid = max(0.1, (r_min + r_max) / 2);
    da = side_sign * (rr / r_mid) * 180 / PI;
    side_center_angle = side_angle_deg + da;
    x0 = -holder_r + (r_min - rr) * cos(side_center_angle);
    y0 = (r_min - rr) * sin(side_center_angle);
    a_clip = max(0.7, floor_blend_angle_pad + 0.35);
    a_eps = 0.35;
    a0_clip = (side_sign > 0) ? (side_angle_deg - a_eps) : (side_angle_deg - a_clip);
    a1_clip = (side_sign > 0) ? (side_angle_deg + a_clip) : (side_angle_deg + a_eps);

    if (rr > 0.2 && r_max > r_min + 0.1) {
        intersection() {
            translate([x0, y0, z_base])
                rotate([0, 90, side_center_angle])
                    cylinder(h = run_len, r = rr, center = false, $fn = max(40, floor($fn / 2)));

            translate([0, 0, z_base - 0.05])
                linear_extrude(height = rr + 0.15)
                    annular_wedge_raw_2d(
                        max(0.1, r_min - rr),
                        r_max + rr,
                        a0_clip,
                        a1_clip,
                        -holder_r
                    );
        }
    }
}

module side_floor_edge_fillet_inner_linear(side_angle_deg, side_sign) {
    side_floor_edge_fillet_linear(side_angle_deg, side_sign, r_front_inner, r_back_inner, floor_thickness);
}

module side_floor_edge_fillet_outer_linear(side_angle_deg, side_sign) {
    side_floor_edge_fillet_linear(side_angle_deg, side_sign, r_front_outer, r_back_outer, 0);
}

module floor_edge_fillet_outer_arc_linear(edge_radius, radial_sign) {
    rr = floor_blend_radius;
    c_r = edge_radius + radial_sign * rr;
    z0 = rr;
    r_band_in = (radial_sign > 0) ? max(0.1, edge_radius - 0.2) : max(0.1, edge_radius - 2 * rr);
    r_band_out = (radial_sign > 0) ? (edge_radius + 2 * rr) : (edge_radius + 0.2);

    if (rr > 0.2 && r_band_out > r_band_in) {
        intersection() {
            translate([-holder_r, 0, z0])
                rotate([0, 0, a_start])
                    rotate_extrude(angle = a_end - a_start)
                        translate([c_r, 0])
                            circle(r = rr, $fn = max(40, floor($fn / 2)));

            translate([0, 0, -0.05])
                linear_extrude(height = rr + 0.15)
                    annular_wedge_2d(
                        r_band_in,
                        r_band_out,
                        a_start - floor_blend_angle_pad,
                        a_end + floor_blend_angle_pad,
                        -holder_r
                    );
        }
    }
}

module holder_shell_linear() {
    difference() {
        linear_extrude(height = back_wall_height)
            annular_wedge_2d(r_front_outer, r_back_outer, a_start, a_end, -holder_r);

        if (back_wall_height > floor_thickness) {
            translate([0, 0, floor_thickness])
                linear_extrude(height = back_wall_height - floor_thickness + 0.05)
                    annular_wedge_2d(r_front_inner, r_back_inner, a_inner_start, a_inner_end, -holder_r);

            interior_floor_blend_subtractor_linear();
        }
    }
}

module top_height_profile_cut_linear() {
    if (back_wall_height > front_wall_height_eff + 0.05) {
        steps = 16;
        r0 = max(0.1, r_front_outer - 2 * wall_thickness);
        r1 = r_back_outer + 2 * wall_thickness;
        z_cap = back_wall_height + max(12, side_top_round_radius + back_rim_round_radius);
        span_r = max(0.1, r_back_outer - r_front_outer);

        profile_pts = concat(
            [[r0, front_wall_height_eff]],
            [for (i = [1 : steps])
                let(
                    t = i / steps,
                    rr = r0 + (r1 - r0) * t,
                    s = smoothstep01((rr - r_front_outer) / span_r),
                    zz = front_wall_height_eff + (back_wall_height - front_wall_height_eff) * s
                )
                [rr, zz]
            ],
            [[r1, z_cap], [r0, z_cap]]
        );

        translate([-holder_r, 0, 0])
            rotate([0, 0, a_start])
                rotate_extrude(angle = a_end - a_start)
                    polygon(points = profile_pts);
    }
}

module front_rim_round_cut_linear() {
    rr = min(
        front_rim_round_radius,
        max_safe_top_round,
        max(0, front_wall_height_eff - floor_thickness - 0.2)
    );
    if (rr > 0 && front_wall_height_eff > floor_thickness) {
        c_r = max(0.1, r_front_inner - rr);
        c_z = front_wall_height_eff - rr;

        translate([-holder_r, 0, c_z])
            rotate([0, 0, a_start])
                rotate_extrude(angle = a_end - a_start)
                    translate([c_r, 0])
                        circle(r = rr, $fn = max(32, floor($fn / 2)));
    }
}

module back_rim_round_cut_linear() {
    rr = min(
        back_rim_round_radius,
        max_safe_top_round,
        max(0, back_wall_height - floor_thickness - 0.2)
    );
    if (rr > 0 && back_wall_height > floor_thickness) {
        c_r = max(0.1, r_back_outer - rr);
        c_z = back_wall_height - rr;

        translate([-holder_r, 0, c_z])
            rotate([0, 0, a_start])
                rotate_extrude(angle = a_end - a_start)
                    translate([c_r, 0])
                        circle(r = rr, $fn = max(32, floor($fn / 2)));
    }
}

module side_top_round_cut_linear(side_angle_deg) {
    rr = min(
        side_top_round_radius,
        max_safe_top_round,
        max(0, back_wall_height - floor_thickness - 0.2)
    );
    if (rr > 0) {
        line_len = max(0.1, (r_back_outer - r_front_outer) + 2 * rr);
        x0 = -holder_r + (r_front_outer - rr) * cos(side_angle_deg);
        y0 = (r_front_outer - rr) * sin(side_angle_deg);
        z_front = max(floor_thickness + rr, front_wall_height_eff - rr);
        z_back = back_wall_height - rr;

        hull() {
            translate([x0, y0, z_front])
                rotate([0, 90, side_angle_deg])
                    cylinder(h = line_len, r = rr, center = false, $fn = max(32, floor($fn / 2)));

            translate([x0, y0, z_back])
                rotate([0, 90, side_angle_deg])
                    cylinder(h = line_len, r = rr, center = false, $fn = max(32, floor($fn / 2)));
        }
    }
}

module front_side_corner_round_cut_linear(side_angle_deg) {
    rr = min(
        front_side_corner_round_radius,
        max_safe_top_round,
        max(0, front_wall_height_eff - floor_thickness - 0.2)
    );
    if (rr > 0 && front_wall_height_eff > floor_thickness) {
        line_len = max(0.1, wall_thickness + 2 * rr);
        x0 = -holder_r + (r_front_outer - rr) * cos(side_angle_deg);
        y0 = (r_front_outer - rr) * sin(side_angle_deg);
        z0 = front_wall_height_eff - rr;

        translate([x0, y0, z0])
            rotate([0, 90, side_angle_deg])
                cylinder(h = line_len, r = rr, center = false, $fn = max(32, floor($fn / 2)));
    }
}

module holder_linear() {
    difference() {
        holder_shell_linear();
        // Keep top opening flat unless explicitly adding top edge rounds.
        front_rim_round_cut_linear();
        back_rim_round_cut_linear();
        side_top_round_cut_linear(a_start);
        side_top_round_cut_linear(a_end);
        front_side_corner_round_cut_linear(a_start);
        front_side_corner_round_cut_linear(a_end);
        side_floor_edge_fillet_inner_linear(a_inner_start, +1);
        side_floor_edge_fillet_inner_linear(a_inner_end, -1);
        side_floor_edge_fillet_outer_linear(a_start, -1);
        side_floor_edge_fillet_outer_linear(a_end, +1);
        floor_edge_fillet_outer_arc_linear(r_front_outer, +1);
        floor_edge_fillet_outer_arc_linear(r_back_outer, -1);
    }
}

module holder_local_placed() {
    translate([0, 0, -back_wall_height])
        holder_linear();
}

module holder_positioned() {
    attachment_frame(attach_angle, holder_r, holder_profile_y_sweep, 0)
        rotate([0, -holder_tilt_deg, 0])
            holder_local_placed();
}

module holder_only_sample() {
    if (holder_only_side_print) {
        rotate([0, 90, 0])
            holder_local_placed();
    } else {
        rotate([0, -holder_tilt_deg, 0])
            holder_local_placed();
    }
}

// -------------------------------
// Output
// -------------------------------
if (render_holder_only) {
    if (show_holder) holder_only_sample();
} else {
    union() {
        clamp_pad_sweep();
        if (show_holder) holder_positioned();
    }
}
