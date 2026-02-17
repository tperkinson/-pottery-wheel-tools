// tool_shelf (v1)
// Curved annular-sector shelf using the canonical C-clamp sweep.

$fn = 180;
include <../../../core_mount_system/c_clamp/v1/c_clamp_profile_topref_v1.scad>;

// -------------------------------
// Quick Tuning (Common)
// -------------------------------
render_holder_only = false; // true = quick holder-only sample

show_clamp = true;
show_pad = true;
show_shelf = true;
show_lips = true;
show_gusset = true;

align_to_sweep_edges = true; // keep shelf sides aligned with clamp sweep ends

sweep_angle = 24;           // deg
radius = 222.25;            // mm
radius_ref_mode = "hook_center"; // "hook_center" or "outer_edge"
axis_z = 0;

pad_length = 35;            // mm
pad_thickness = 4;          // mm
pad_overlap = 1.0;          // mm
pad_offset_y = 0;           // keep 0 to preserve top reference

holder_top_offset = 0;      // mm from clamp top (max_profile_y)
holder_tilt_deg = 4;        // deg (positive drains toward clamp side)
holder_angle_offset = 0;    // deg tangent offset within sweep
holder_radial_location_on_pad = 0; // mm from clamp wall to inner shelf edge

arc_length = 152.4;         // mm (6")
radial_width = 152.4;       // mm (6")
floor_thickness = 4;        // mm
lip_thickness = 3;          // mm
lip_height_near = 14;       // mm (edge near user)
lip_height_far = 6;         // mm (edge near clamp / drain)
lip_height_sides = 12;      // mm (radial wall at sweep start)
lip_height_side_end = lip_height_sides; // mm (radial wall at sweep end)
side_wall_thickness = lip_thickness; // mm (angular thickness of radial walls)
side_wall_drop = 10;        // mm (radial walls + inner wall drop below floor)
corner_radius = 8;          // mm (floor fillet)
lip_corner_radius = 6;      // mm (lip fillet)
corner_gap_size = 5;        // mm (gap at inner-wall/side-wall corners)
inner_overhang = 6;         // mm (extend shelf inward over clamp)

// Gusset / brace (single ramped web for side printing)
gusset_thickness = 6;       // mm (minimum radial run target)
gusset_height = 25;         // mm (drop below floor)
gusset_width = 45;          // mm (tangent span)
gusset_back_overhang = 4;   // mm (extra run toward shelf interior)
gusset_flare = 8;           // mm (extra base run)
gusset_max_overhang_deg = 45; // deg (ramp limit for side print)
gusset_attach_overlap = 2;  // mm (embed into clamp wall)
gusset_top_flat = 2;        // mm (short contact flat under floor)

// Clamp-side reinforcement / drain channel
clamp_cap_thickness = 3;    // mm
clamp_cap_width = 18;       // mm
enable_clamp_channel = false;
clamp_channel_width = 10;   // mm
clamp_channel_depth = 2.0;  // mm
clamp_channel_offset = 0;   // mm

max_projection = 127;       // mm from pad outer edge

// Drain notch at low clamp-side wall
enable_drain_notch = true;
drain_notch_width = 8;      // mm along tangent

// -------------------------------
// Strength / Printability Checks
// -------------------------------
min_floor_thickness_recommended = 2.0;
min_lip_thickness_recommended = 2.0;
min_gusset_thickness_recommended = 4.0;
min_gusset_height_recommended = 18.0;
mount_flat_wall_height_available = 45.4;

// -------------------------------
// Advanced Controls / Debug
// -------------------------------
show_profile = false;
show_axis = true;
show_attach_marker = false;
axis_marker_r = 1.5;
attach_marker_r = 1.0;

// -------------------------------
// Derived
// -------------------------------
radius_ref_x = (radius_ref_mode == "hook_center") ? hook_center_x : max_profile_x;
axis_x = radius_ref_x - radius;
axis_shift_x = max(0, axis_x - min_profile_x + 0.1);

mount_wall_radius = axis_shift_x + (max_profile_x - axis_x);
pad_outer_radius = mount_wall_radius + pad_length;

holder_origin_x = max_profile_x + holder_radial_location_on_pad;
holder_profile_y_2d = max_profile_y + holder_top_offset;
holder_profile_y_sweep = holder_profile_y_2d - axis_z;

inner_radius = mount_wall_radius + holder_radial_location_on_pad - inner_overhang;
outer_radius = inner_radius + radial_width;
centerline_radius = (inner_radius + outer_radius) / 2;

arc_angle_deg = (centerline_radius > 0) ? (arc_length / centerline_radius) * 180 / PI : 0;
shelf_angle_deg = align_to_sweep_edges ? sweep_angle : arc_angle_deg;
attach_angle = sweep_angle / 2 + holder_angle_offset;

a_start = -shelf_angle_deg / 2;
a_end = shelf_angle_deg / 2;

shelf_start_angle = attach_angle + a_start;
shelf_end_angle = attach_angle + a_end;

projection_from_pad_outer = outer_radius - pad_outer_radius;

side_wall_angle_deg = (centerline_radius > 0)
    ? max(0.4, (side_wall_thickness / centerline_radius) * 180 / PI)
    : 0.4;

gap_angle_deg = (inner_radius > 0)
    ? (corner_gap_size / inner_radius) * 180 / PI
    : 0;

corner_radius_eff = (corner_radius > 0)
    ? min(corner_radius, max(0, radial_width / 2 - 0.2))
    : 0;

lip_corner_radius_eff = (lip_corner_radius > 0)
    ? min(lip_corner_radius, max(0, lip_thickness / 2 - 0.1))
    : 0;

arc_length_in = arc_length / 25.4;
radial_width_in = radial_width / 25.4;
arc_length_effective = (centerline_radius > 0) ? (shelf_angle_deg * PI / 180) * centerline_radius : 0;
arc_length_effective_in = arc_length_effective / 25.4;

lip_height_max = max(lip_height_near, max(lip_height_far, max(lip_height_sides, lip_height_side_end)));

gusset_top_flat_eff = max(gusset_top_flat, gusset_thickness);
gusset_depth = max(0, max(gusset_thickness, inner_overhang + gusset_back_overhang));
gusset_base_min = (gusset_max_overhang_deg > 0)
    ? (gusset_top_flat_eff + (gusset_height / tan(gusset_max_overhang_deg)))
    : 0;
gusset_base_span = max(gusset_depth + gusset_flare, gusset_base_min);

gusset_r0 = max(0.1, mount_wall_radius - gusset_attach_overlap);
gusset_r1 = min(outer_radius, gusset_r0 + gusset_base_span);
gusset_span_angle = (mount_wall_radius > 0)
    ? (gusset_width / mount_wall_radius) * 180 / PI
    : 0;
gusset_a0 = max(a_start, -gusset_span_angle / 2);
gusset_a1 = min(a_end, gusset_span_angle / 2);

mask_r_in = min(inner_radius, gusset_r0 - 0.4);
mask_r_out = outer_radius + lip_thickness + 0.5;
mask_z0 = -floor_thickness - side_wall_drop - gusset_height - 1.0;
mask_height = lip_height_max + clamp_cap_thickness + floor_thickness + side_wall_drop + gusset_height + 2.0;

if (projection_from_pad_outer > max_projection)
    echo("WARNING: projection exceeds max_projection.");
if (floor_thickness < min_floor_thickness_recommended)
    echo("WARNING: floor_thickness is thin for PLA/PETG.");
if (lip_thickness < min_lip_thickness_recommended)
    echo("WARNING: lip_thickness is thin for PLA/PETG.");
if (gusset_thickness < min_gusset_thickness_recommended)
    echo("WARNING: gusset_thickness is thin for PLA/PETG.");
if (gusset_height < min_gusset_height_recommended)
    echo("WARNING: gusset_height is low for wet loads.");
if (holder_radial_location_on_pad < 0 || holder_radial_location_on_pad > pad_length)
    echo("WARNING: holder_radial_location_on_pad is outside pad_length.");
if (inner_radius <= 0 || outer_radius <= inner_radius || shelf_angle_deg <= 0)
    echo("WARNING: invalid annular-sector geometry.");
if (align_to_sweep_edges && abs(holder_angle_offset) > 0.01)
    echo("WARNING: holder_angle_offset breaks sweep-edge alignment.");
if (align_to_sweep_edges && abs(arc_length_effective - arc_length) > 0.5)
    echo("WARNING: arc_length differs from sweep-aligned effective arc length.");
if (gusset_base_span + 0.1 < gusset_base_min)
    echo("WARNING: gusset slope may be steep for side printing.");
if (gusset_r1 <= gusset_r0 + 0.2)
    echo("WARNING: gusset span collapsed; check gusset dimensions.");
if (max(lip_height_far, lip_height_sides) > mount_flat_wall_height_available + 5)
    echo("WARNING: lip heights may interfere with clamp region.");

// -------------------------------
// SCAD Reporting
// -------------------------------
echo(str("arc_length_in = ", arc_length_in));
echo(str("radial_width_in = ", radial_width_in));
echo(str("arc_length_effective_in = ", arc_length_effective_in));

function arc_point(r, a_deg, cx) = [cx + r * cos(a_deg), r * sin(a_deg)];
function arc_points(r, a0_deg, a1_deg, n, cx) =
    [for (i = [0 : n]) arc_point(r, a0_deg + (a1_deg - a0_deg) * i / n, cx)];
function seg_count_for_span(a0_deg, a1_deg) = max(12, ceil(abs(a1_deg - a0_deg) / 3));

foot_n = seg_count_for_span(shelf_start_angle, shelf_end_angle);
foot_points = (shelf_angle_deg > 0 && outer_radius > inner_radius)
    ? concat(
        arc_points(outer_radius, shelf_start_angle, shelf_end_angle, foot_n, -mount_wall_radius),
        arc_points(inner_radius, shelf_end_angle, shelf_start_angle, foot_n, -mount_wall_radius)
      )
    : [];

foot_min_x = (len(foot_points) > 0) ? min([for (p = foot_points) p[0]]) : 0;
foot_max_x = (len(foot_points) > 0) ? max([for (p = foot_points) p[0]]) : 0;
foot_min_y = (len(foot_points) > 0) ? min([for (p = foot_points) p[1]]) : 0;
foot_max_y = (len(foot_points) > 0) ? max([for (p = foot_points) p[1]]) : 0;

footprint_x = foot_max_x - foot_min_x;
footprint_y = foot_max_y - foot_min_y;
footprint_x_in = footprint_x / 25.4;
footprint_y_in = footprint_y / 25.4;

echo(str("footprint_mm = ", [footprint_x, footprint_y]));
echo(str("footprint_in = ", [footprint_x_in, footprint_y_in]));

if (footprint_x > 220 || footprint_y > 220)
    echo("WARNING: footprint exceeds 220x220 bed.");

// -------------------------------
// Helpers
// -------------------------------
module annular_sector_span_2d(r_in, r_out, a0_deg, a1_deg, axis_r = mount_wall_radius) {
    if (r_out > r_in && abs(a1_deg - a0_deg) > 0.01) {
        cx = -axis_r;
        n = seg_count_for_span(a0_deg, a1_deg);

        polygon(points = concat(
            arc_points(r_out, a0_deg, a1_deg, n, cx),
            arc_points(r_in, a1_deg, a0_deg, n, cx)
        ));
    }
}

module annular_sector_span_2d_rounded(r_in, r_out, a0_deg, a1_deg, axis_r, fillet_r) {
    if (fillet_r > 0) {
        offset(r = fillet_r)
            offset(r = -fillet_r)
                annular_sector_span_2d(r_in, r_out, a0_deg, a1_deg, axis_r);
    } else {
        annular_sector_span_2d(r_in, r_out, a0_deg, a1_deg, axis_r);
    }
}

module wall_band(r_in, r_out, h, a0 = a_start, a1 = a_end, z0 = 0, fillet = 0) {
    if (h > 0 && r_out > r_in && a1 > a0) {
        translate([0, 0, z0])
            linear_extrude(height = h)
                annular_sector_span_2d_rounded(r_in, r_out, a0, a1, mount_wall_radius, fillet);
    }
}

// -------------------------------
// Clamp / Pad Geometry (swept)
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

// local +X = radial outward, +Y = tangent, +Z = profile-up
module attachment_frame(angle_deg, radial_r, profile_y, tangent = 0) {
    rotate([90, 0, 0])
        rotate([0, 0, angle_deg])
            translate([radial_r, tangent, profile_y])
                children();
}

// -------------------------------
// Shelf Geometry (linear, non-swept)
// -------------------------------
module shelf_floor_linear() {
    translate([0, 0, -floor_thickness])
        linear_extrude(height = floor_thickness)
            annular_sector_span_2d_rounded(inner_radius, outer_radius, a_start, a_end, mount_wall_radius, corner_radius_eff);
}

module shelf_lips_linear() {
    inner_a0 = a_start + gap_angle_deg;
    inner_a1 = a_end - gap_angle_deg;

    wall_band(inner_radius, inner_radius + lip_thickness, lip_height_far, inner_a0, inner_a1, 0, lip_corner_radius_eff);
    wall_band(outer_radius - lip_thickness, outer_radius, lip_height_near, a_start, a_end, 0, lip_corner_radius_eff);

    wall_band(inner_radius, outer_radius, lip_height_sides, a_start, min(a_end, a_start + side_wall_angle_deg), 0, lip_corner_radius_eff);
    wall_band(inner_radius, outer_radius, lip_height_side_end, max(a_start, a_end - side_wall_angle_deg), a_end, 0, lip_corner_radius_eff);

    wall_band(inner_radius, outer_radius, side_wall_drop, a_start, min(a_end, a_start + side_wall_angle_deg), -floor_thickness - side_wall_drop, lip_corner_radius_eff);
    wall_band(inner_radius, outer_radius, side_wall_drop, max(a_start, a_end - side_wall_angle_deg), a_end, -floor_thickness - side_wall_drop, lip_corner_radius_eff);
    wall_band(inner_radius, inner_radius + lip_thickness, side_wall_drop, inner_a0, inner_a1, -floor_thickness - side_wall_drop, lip_corner_radius_eff);
}

module shelf_clamp_cap_linear() {
    cap_r1 = min(outer_radius, inner_radius + clamp_cap_width);
    wall_band(inner_radius, cap_r1, clamp_cap_thickness, a_start, a_end, 0, lip_corner_radius_eff);
}

module shelf_gusset_linear() {
    if (show_gusset && gusset_height > 0 && gusset_a1 > gusset_a0 && gusset_r1 > gusset_r0 + 0.2) {
        top_r1 = min(gusset_r1, gusset_r0 + gusset_top_flat_eff);

        hull() {
            translate([0, 0, -floor_thickness])
                linear_extrude(height = 0.2)
                    annular_sector_span_2d(gusset_r0, top_r1, gusset_a0, gusset_a1, mount_wall_radius);

            translate([0, 0, -floor_thickness - gusset_height])
                linear_extrude(height = 0.2)
                    annular_sector_span_2d(gusset_r0, gusset_r1, gusset_a0, gusset_a1, mount_wall_radius);
        }
    }
}

module shelf_drain_notch_cut() {
    if (enable_drain_notch && lip_height_far > 0 && lip_thickness > 0 && drain_notch_width > 0) {
        notch_x0 = -mount_wall_radius + inner_radius - 0.5;
        notch_w = lip_thickness + 1.0;
        notch_h = lip_height_far + floor_thickness + 1.0;
        notch_z0 = -floor_thickness - 0.5;

        translate([notch_x0, -drain_notch_width / 2, notch_z0])
            cube([notch_w, drain_notch_width, notch_h], center = false);
    }
}

module shelf_clamp_channel_cut() {
    if (enable_clamp_channel && clamp_channel_depth > 0 && clamp_channel_width > 0 && clamp_cap_width > 0) {
        channel_r1 = min(outer_radius, inner_radius + clamp_cap_width);
        channel_w = max(0.1, channel_r1 - inner_radius);
        channel_x0 = -mount_wall_radius + inner_radius;
        channel_z0 = max(0, clamp_cap_thickness - clamp_channel_depth);

        translate([channel_x0, clamp_channel_offset - clamp_channel_width / 2, channel_z0])
            cube([channel_w, clamp_channel_width, clamp_channel_depth + 0.5], center = false);
    }
}

module shelf_linear() {
    intersection() {
        difference() {
            union() {
                shelf_floor_linear();
                if (show_lips)
                    shelf_lips_linear();
                shelf_clamp_cap_linear();
                shelf_gusset_linear();
            }

            shelf_drain_notch_cut();
            shelf_clamp_channel_cut();
        }

        translate([0, 0, mask_z0])
            linear_extrude(height = mask_height)
                annular_sector_span_2d(mask_r_in, mask_r_out, a_start, a_end, mount_wall_radius);
    }
}

module shelf_local_placed() {
    shelf_linear();
}

module shelf_positioned() {
    attachment_frame(attach_angle, mount_wall_radius, holder_profile_y_sweep, 0)
        rotate([0, -holder_tilt_deg, 0])
            shelf_local_placed();
}

module shelf_only_sample() {
    rotate([0, -holder_tilt_deg, 0])
        shelf_local_placed();
}

// -------------------------------
// Output
// -------------------------------
if (show_profile) {
    translate([axis_shift_x, 0])
        translate([-axis_x, -axis_z])
            clamp_pad_profile();

    if (show_attach_marker) {
        color("orange")
            translate([axis_shift_x, 0])
                translate([-axis_x, -axis_z])
                    translate([holder_origin_x, holder_profile_y_2d])
                        circle(r = attach_marker_r, $fn = 36);
    }

    if (show_axis) {
        color("red")
            translate([axis_shift_x, 0])
                circle(r = axis_marker_r, $fn = 48);
    }
} else {
    if (render_holder_only) {
        if (show_shelf) shelf_only_sample();
    } else {
        union() {
            clamp_pad_sweep();
            if (show_shelf) shelf_positioned();
        }
    }
}
