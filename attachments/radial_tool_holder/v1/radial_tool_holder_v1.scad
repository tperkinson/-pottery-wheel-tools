// radial_tool_holder (v1)
// Curved annular-sector multi-compartment holder using canonical C-clamp sweep.
// Design intent: arc_length drives holder sweep, and the mount flat wall is reused
// as the container front wall (shared wall) in the full assembly.

$fn = 180;
include <../../../core_mount_system/c_clamp/v1/c_clamp_profile_topref_v1.scad>;

// -------------------------------
// Quick Tuning (Common)
// -------------------------------
render_holder_only = false;                 // true = quick holder-only sample
holder_only_with_shared_wall_proxy = true;   // add proxy wall in holder-only mode

show_clamp = true;
show_pad = false;                            // disable by default to avoid top access blockage
show_holder = true;
show_holder_shell = true;
show_holder_side_walls = true;
show_holder_dividers = true;
show_holder_blend = true;
show_holder_gusset = true;

radius = 222.25;                             // mm
radius_ref_mode = "hook_center";             // "hook_center" or "outer_edge"
axis_z = 0;

pad_length = 8;
pad_thickness = 4;
pad_overlap = 1.0;
pad_offset_y = 0;                            // keep 0 for top-reference behavior

// Container top placement relative to clamp top (max_profile_y).
// Default 0 means container top rim is aligned with clamp top.
container_top_offset = 0;
holder_tilt_deg = 0;
holder_angle_offset = 0;                     // tangent rotation offset within sweep

// Annular-sector container controls
arc_length = 105;                            // mm, centerline arc length (drives sweep)
radial_width = 32;                           // mm
holder_radial_location_on_pad = radial_width / 2;
depth = 32;                                  // mm, vertical depth down from top rim

wall_thickness = 3.0;
floor_thickness = 3.2;
compartment_count = 2;
divider_thickness = 2.4;

// Drain holes (one per compartment, bottom-centered with optional offsets)
enable_drain_holes = true;
drain_hole_diameter = 4.0;
drain_hole_radial_offset = 0.0;              // +outward / -inward from compartment center
drain_hole_arc_offset = 0.0;                 // mm along arc, +toward sweep end / -toward start

// Shared-wall interface controls
shared_wall_overlap = 1.0;                   // mm radial merge into mount wall
shared_wall_height = depth;                  // mm of shared front-wall engagement
shared_wall_blend_radius = 2.0;              // mm local blend/thickening at interface

// Optional reinforcement at mount interface
enable_mount_gusset = false;
mount_gusset_tangent_width = 16;
mount_gusset_base_depth = 8;
mount_gusset_base_height = 3;
mount_gusset_top_depth = 4;
mount_gusset_top_height = 9;
mount_gusset_angle_offset = 0;

// -------------------------------
// Advanced Controls / Debug
// -------------------------------
show_profile = false;
show_axis = true;
show_attach_marker = false;
axis_marker_r = 1.5;
attach_marker_r = 1.0;

mount_flat_wall_height_available = 45.4;     // approx flat-wall height at max_profile_x
min_compartment_arc_length = 6.0;
max_recommended_overlap = 4.0;
join_eps = 0.05;

// -------------------------------
// Derived
// -------------------------------
radius_ref_x = (radius_ref_mode == "hook_center") ? hook_center_x : max_profile_x;
axis_x = radius_ref_x - radius;
axis_shift_x = max(0, axis_x - min_profile_x + 0.1);

shared_wall_attach_x = max_profile_x;
shared_wall_top_profile_y_2d = max_profile_y + container_top_offset;
shared_wall_top_profile_y_sweep = shared_wall_top_profile_y_2d - axis_z;
shared_wall_radius = axis_shift_x + (shared_wall_attach_x - axis_x);

centerline_radius = shared_wall_radius + holder_radial_location_on_pad;
arc_angle_deg = (centerline_radius > 0) ? (arc_length / centerline_radius) * 180 / PI : 0;

// arc_length fully defines holder sweep angle
sweep_angle_effective = arc_angle_deg;
attach_angle_effective = sweep_angle_effective / 2 + holder_angle_offset;

inner_radius = centerline_radius - radial_width / 2;
outer_radius = centerline_radius + radial_width / 2;

// The shell extrusion includes bottom + back wall + shared front-wall merge strip.
body_inner_radius = inner_radius - shared_wall_overlap;
body_outer_radius = outer_radius;
cavity_inner_radius = inner_radius;
cavity_outer_radius = outer_radius - wall_thickness;

divider_count = max(0, compartment_count - 1);
divider_ref_radius = (cavity_inner_radius + cavity_outer_radius) / 2;
divider_step_deg = (compartment_count > 0) ? arc_angle_deg / compartment_count : 0;

a_start = -arc_angle_deg / 2;
a_end = arc_angle_deg / 2;

end_wall_angle_thickness = (divider_ref_radius > 0) ? (wall_thickness / divider_ref_radius) * 180 / PI : 0;
divider_angle_thickness = (divider_ref_radius > 0) ? (divider_thickness / divider_ref_radius) * 180 / PI : 0;

holder_start_angle = attach_angle_effective + a_start;
holder_end_angle = attach_angle_effective + a_end;

compartment_arc_length = (compartment_count > 0) ? (arc_length / compartment_count) : 0;
required_arc_for_walls_and_dividers =
    2 * wall_thickness + divider_count * divider_thickness + compartment_count * min_compartment_arc_length;

interior_height = max(0, depth - floor_thickness);
front_strip_height = min(depth, shared_wall_height);

edge_opening_arc_est = compartment_arc_length - wall_thickness - divider_thickness / 2;
middle_opening_arc_est = compartment_arc_length - divider_thickness;
single_opening_arc_est = arc_length - 2 * wall_thickness;
min_compartment_opening_arc_est = (compartment_count <= 1)
    ? single_opening_arc_est
    : min(edge_opening_arc_est, middle_opening_arc_est);

drain_hole_radius_nominal = divider_ref_radius + drain_hole_radial_offset;
drain_hole_angle_offset_deg = (drain_hole_radius_nominal > 0)
    ? (drain_hole_arc_offset / drain_hole_radius_nominal) * 180 / PI
    : 0;

if (wall_thickness < 2.0)
    echo("WARNING: wall_thickness is very thin (<2.0 mm).");
if (divider_thickness < 1.6)
    echo("WARNING: divider_thickness is very thin (<1.6 mm).");
if (floor_thickness < 2.0)
    echo("WARNING: floor_thickness is very thin (<2.0 mm).");

if (compartment_count < 1)
    echo("WARNING: compartment_count must be >= 1.");
if (arc_length <= required_arc_for_walls_and_dividers)
    echo("WARNING: impossible compartment packing for current arc_length / thickness settings.");
if (divider_count > 0 && compartment_arc_length <= divider_thickness + 0.6)
    echo("WARNING: impossible compartment packing: divider spacing is too small.");

if (centerline_radius <= 0 || inner_radius <= 0 || outer_radius <= inner_radius || arc_angle_deg <= 0)
    echo("WARNING: self-intersection risk from invalid annular-sector radii or arc angle.");
if (arc_angle_deg >= 175)
    echo("WARNING: self-intersection risk: arc_angle_deg is too large.");
if (cavity_outer_radius <= cavity_inner_radius)
    echo("WARNING: self-intersection risk: radial_width too small for requested wall thickness.");
if (depth <= floor_thickness)
    echo("WARNING: self-intersection risk: depth must be > floor_thickness.");
if (body_inner_radius <= 0)
    echo("WARNING: self-intersection risk: shared-wall overlap pushes body across sweep axis.");

if (holder_start_angle < 0 || holder_end_angle > sweep_angle_effective)
    echo("WARNING: clamp/pad interference risk: holder arc exceeds swept clamp span.");
if (container_top_offset > 4)
    echo("WARNING: clamp/pad interference risk: container top is far above clamp top.");
if (container_top_offset - depth < min_profile_y + 2)
    echo("WARNING: clamp/pad interference risk: holder depth reaches below clamp profile bounds.");
if (shared_wall_overlap > max_recommended_overlap)
    echo("WARNING: clamp/pad interference risk: shared_wall_overlap is larger than recommended.");
if (show_pad && pad_length > holder_radial_location_on_pad + wall_thickness)
    echo("WARNING: clamp/pad interference risk: pad overhang may block top access to compartments.");

if (shared_wall_overlap < 0)
    echo("WARNING: invalid shared-wall overlap: must be >= 0.");
if (shared_wall_overlap < 0.4)
    echo("WARNING: invalid shared-wall overlap: too low for robust shared load path.");
if (shared_wall_height <= floor_thickness)
    echo("WARNING: invalid shared-wall height: must exceed floor_thickness.");
if (shared_wall_height > mount_flat_wall_height_available + 0.1)
    echo("WARNING: invalid shared-wall height: exceeds available mount flat wall height.");
if (inner_radius > shared_wall_radius + 0.25)
    echo("WARNING: invalid shared-wall overlap: inner radius no longer intersects mount wall.");

if (enable_drain_holes && drain_hole_diameter <= 0)
    echo("WARNING: invalid drain_hole_diameter: must be > 0.");
if (enable_drain_holes && drain_hole_radius_nominal - drain_hole_diameter / 2 <= cavity_inner_radius)
    echo("WARNING: drain-hole placement invalid: hole intersects inner/front wall.");
if (enable_drain_holes && drain_hole_radius_nominal + drain_hole_diameter / 2 >= cavity_outer_radius)
    echo("WARNING: drain-hole placement invalid: hole intersects outer/back wall.");
if (enable_drain_holes && drain_hole_diameter > min_compartment_opening_arc_est)
    echo("WARNING: drain-hole placement invalid: hole too large for compartment arc opening.");
if (enable_drain_holes && abs(drain_hole_arc_offset) > max(0, (min_compartment_opening_arc_est - drain_hole_diameter) / 2))
    echo("WARNING: drain-hole placement invalid: drain_hole_arc_offset shifts hole outside compartment center zone.");

// -------------------------------
// Helpers
// -------------------------------
function arc_angle_from_length(len, r) = (r > 0) ? (len / r) * 180 / PI : 0;
function arc_point(r, a_deg, cx) = [cx + r * cos(a_deg), r * sin(a_deg)];
function arc_points(r, a0_deg, a1_deg, n, cx) =
    [for (i = [0 : n]) arc_point(r, a0_deg + (a1_deg - a0_deg) * i / n, cx)];
function seg_count_for_span(a0_deg, a1_deg) = max(12, ceil(abs(a1_deg - a0_deg) / 3));
function comp_left_angle(i) =
    (i <= 0)
    ? (a_start + end_wall_angle_thickness)
    : (a_start + divider_step_deg * i + divider_angle_thickness / 2);
function comp_right_angle(i) =
    (i >= compartment_count - 1)
    ? (a_end - end_wall_angle_thickness)
    : (a_start + divider_step_deg * (i + 1) - divider_angle_thickness / 2);

module annular_sector_span_2d(r_in, r_out, a0_deg, a1_deg, axis_r = shared_wall_radius) {
    if (r_out > r_in && abs(a1_deg - a0_deg) > 0.01) {
        cx = -axis_r;
        n = seg_count_for_span(a0_deg, a1_deg);

        polygon(points = concat(
            arc_points(r_out, a0_deg, a1_deg, n, cx),
            arc_points(r_in, a1_deg, a0_deg, n, cx)
        ));
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
        rotate_extrude(angle = sweep_angle_effective)
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
// Holder Geometry (linear, non-swept)
// -------------------------------
module holder_shell_extruded_linear() {
    // Single extrusion/difference: bottom + back wall + shared front-wall strip.
    difference() {
        linear_extrude(height = depth)
            annular_sector_span_2d(body_inner_radius, body_outer_radius, a_start, a_end);

        if (interior_height > 0) {
            open_a0 = a_start - end_wall_angle_thickness;
            open_a1 = a_end + end_wall_angle_thickness;
            translate([0, 0, floor_thickness])
                linear_extrude(height = interior_height)
                    annular_sector_span_2d(cavity_inner_radius, cavity_outer_radius, open_a0, open_a1);
        }

        // Trim the extra shared-front strip above requested shared wall height.
        if (front_strip_height < depth) {
            translate([0, 0, front_strip_height])
                linear_extrude(height = depth - front_strip_height)
                    annular_sector_span_2d(body_inner_radius, cavity_inner_radius, a_start, a_end);
        }
    }
}

module holder_side_walls_linear() {
    side_h = max(0, depth - floor_thickness + join_eps);
    wall_a = max(0.1, end_wall_angle_thickness);
    wall_join_a = arc_angle_from_length(0.2, centerline_radius);

    if (side_h > 0) {
        translate([0, 0, floor_thickness - join_eps])
            linear_extrude(height = side_h)
                annular_sector_span_2d(body_inner_radius, body_outer_radius, a_start - wall_join_a, min(a_end + wall_join_a, a_start + wall_a));

        translate([0, 0, floor_thickness - join_eps])
            linear_extrude(height = side_h)
                annular_sector_span_2d(body_inner_radius, body_outer_radius, max(a_start - wall_join_a, a_end - wall_a), a_end + wall_join_a);
    }
}

module holder_dividers_linear() {
    div_h = max(0, depth - floor_thickness + join_eps);
    div_r0 = max(body_inner_radius, cavity_inner_radius - join_eps);
    div_r1 = min(body_outer_radius, cavity_outer_radius + join_eps);

    if (divider_count > 0 && div_h > 0) {
        for (i = [1 : divider_count]) {
            a_mid = a_start + divider_step_deg * i;
            a0 = max(a_start, a_mid - divider_angle_thickness / 2);
            a1 = min(a_end, a_mid + divider_angle_thickness / 2);

            translate([0, 0, floor_thickness - join_eps])
                linear_extrude(height = div_h)
                    annular_sector_span_2d(div_r0, div_r1, a0, a1);
        }
    }
}

module shared_wall_blend_linear() {
    if (shared_wall_blend_radius > 0) {
        blend_outer = min(cavity_outer_radius, cavity_inner_radius + shared_wall_blend_radius);
        blend_h = min(front_strip_height, floor_thickness + shared_wall_blend_radius);

        if (blend_outer > body_inner_radius && blend_h > 0) {
            linear_extrude(height = blend_h)
                annular_sector_span_2d(body_inner_radius, blend_outer, a_start, a_end);
        }
    }
}

module holder_mount_gusset_linear() {
    if (enable_mount_gusset && show_holder_gusset) {
        half_gusset_angle = arc_angle_from_length(mount_gusset_tangent_width / 2, centerline_radius);
        gusset_a0 = max(a_start, mount_gusset_angle_offset - half_gusset_angle);
        gusset_a1 = min(a_end, mount_gusset_angle_offset + half_gusset_angle);

        base_r0 = body_inner_radius;
        base_r1 = min(cavity_outer_radius, base_r0 + mount_gusset_base_depth);
        top_r1 = min(base_r1, base_r0 + mount_gusset_top_depth);

        top_z0 = max(floor_thickness, depth - mount_gusset_top_height);

        if (gusset_a1 > gusset_a0 && base_r1 > base_r0 && top_r1 > base_r0) {
            hull() {
                linear_extrude(height = mount_gusset_base_height)
                    annular_sector_span_2d(base_r0, base_r1, gusset_a0, gusset_a1);

                translate([0, 0, top_z0])
                    linear_extrude(height = mount_gusset_top_height)
                        annular_sector_span_2d(base_r0, top_r1, gusset_a0, gusset_a1);
            }
        }
    }
}

module holder_drain_holes_linear() {
    if (enable_drain_holes && compartment_count > 0 && drain_hole_diameter > 0) {
        for (i = [0 : compartment_count - 1]) {
            a_l = comp_left_angle(i);
            a_r = comp_right_angle(i);
            a_mid = (a_l + a_r) / 2 + drain_hole_angle_offset_deg;
            r_mid = drain_hole_radius_nominal;
            x_mid = -shared_wall_radius + r_mid * cos(a_mid);
            y_mid = r_mid * sin(a_mid);

            translate([x_mid, y_mid, -join_eps])
                cylinder(h = floor_thickness + 2 * join_eps, d = drain_hole_diameter, center = false, $fn = max(24, floor($fn / 3)));
        }
    }
}

module holder_linear() {
    difference() {
        union() {
            if (show_holder_shell) holder_shell_extruded_linear();
            if (show_holder_side_walls) holder_side_walls_linear();
            if (show_holder_dividers) holder_dividers_linear();
            if (show_holder_blend) shared_wall_blend_linear();
            holder_mount_gusset_linear();
        }

        holder_drain_holes_linear();
    }
}

module shared_wall_proxy_linear() {
    proxy_thickness = max(0.8, wall_thickness);
    proxy_h = min(depth, shared_wall_height);

    if (proxy_h > 0) {
        linear_extrude(height = proxy_h)
            annular_sector_span_2d(max(0.1, body_inner_radius - proxy_thickness), body_inner_radius, a_start, a_end);
    }
}

module holder_local_placed() {
    // Container opens at Z=0 and drops downward by depth.
    translate([0, 0, -depth])
        holder_linear();
}

module holder_positioned() {
    attachment_frame(attach_angle_effective, shared_wall_radius, shared_wall_top_profile_y_sweep, 0)
        rotate([0, holder_tilt_deg, 0])
            holder_local_placed();
}

module holder_only_sample() {
    rotate([0, holder_tilt_deg, 0])
        union() {
            holder_local_placed();
            if (holder_only_with_shared_wall_proxy)
                translate([0, 0, -depth])
                    shared_wall_proxy_linear();
        }
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
                    translate([shared_wall_attach_x, shared_wall_top_profile_y_2d])
                        circle(r = attach_marker_r, $fn = 36);
    }

    if (show_axis) {
        color("red")
            translate([axis_shift_x, 0])
                circle(r = axis_marker_r, $fn = 48);
    }
} else {
    if (render_holder_only) {
        if (show_holder) holder_only_sample();
    } else {
        union() {
            clamp_pad_sweep();
            if (show_holder) holder_positioned();
        }
    }
}
