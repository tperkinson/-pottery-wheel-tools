// throwing_towel_holder (v1)
// Sturdy radial drape bar with shared-wall mount using the canonical C-clamp sweep.

$fn = 180;
include <../../../core_mount_system/c_clamp/v1/c_clamp_profile_topref_v1.scad>;

// -------------------------------
// Quick Tuning (Common)
// -------------------------------
render_holder_only = false; // true = quick holder-only sample print

show_clamp = true;
show_pad = true;
show_holder = true;
show_gussets = true;
show_bar = true;
show_retention = true;
show_end_stop = true;

sweep_angle = 24;           // deg
radius = 222.25;            // mm
radius_ref_mode = "hook_center"; // "hook_center" or "outer_edge"
axis_z = 0;

pad_length = 30;            // mm
pad_thickness = 4;          // mm
pad_overlap = 1.0;          // mm
pad_offset_y = 0;           // keep 0 to preserve top reference

holder_radial_location_on_pad = pad_length; // mm, location from clamp wall
holder_top_offset = 0;      // mm from clamp top
holder_tilt_deg = 0;        // deg
holder_angle_offset = 0;    // deg tangent offset within sweep

bar_length = 110;           // mm
bar_diameter = 20;          // mm
bar_start_offset = 10;      // mm from pad outer edge
bar_center_height = 18;     // mm above pad plane

retention_lip_height = 1.5; // mm
retention_lip_width = 4;    // mm (tangent width)

end_stop_diameter = 26;     // mm
end_stop_length = 6;        // mm

gusset_thickness = 6;       // mm (tangent thickness of each gusset plate)
gusset_height = 25;         // mm
gusset_width = 40;          // mm (overall gusset span in tangent direction)

max_projection = 127;       // mm from pad outer edge

// -------------------------------
// Strength / Printability (Common)
// -------------------------------
shared_wall_overlap = 1.0;  // mm overlap into C-cup flat wall
min_bar_diameter_recommended = 16;
min_gusset_thickness_recommended = 4;
min_gusset_height_recommended = 18;
mount_flat_wall_height_available = 45.4;
join_eps = 0.05;

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

pad_outer_x = max_profile_x + pad_length;
holder_origin_x = max_profile_x + holder_radial_location_on_pad;

holder_profile_y_2d = max_profile_y + holder_top_offset;
holder_profile_y_sweep = holder_profile_y_2d - axis_z;
holder_r = axis_shift_x + (holder_origin_x - axis_x);

attach_angle = sweep_angle / 2 + holder_angle_offset;

wall_local_x = max_profile_x - holder_origin_x;
pad_outer_local_x = pad_outer_x - holder_origin_x;

bar_radius = bar_diameter / 2;
bar_start_local_x = pad_outer_local_x + bar_start_offset;
bar_end_local_x = bar_start_local_x + bar_length;
bar_start_local_x_geom = bar_start_local_x - join_eps;
bar_length_geom = bar_length + 2 * join_eps;
bar_end_local_x_geom = bar_start_local_x_geom + bar_length_geom;
bar_end_stop_outer_x = bar_end_local_x + end_stop_length + join_eps;

bar_projection_from_pad_outer = bar_end_stop_outer_x - pad_outer_local_x;

lip_margin = 2.0;
lip_length = max(0, bar_length - end_stop_length - 2 * lip_margin);
lip_start_x = bar_start_local_x + lip_margin;
lip_start_z = bar_center_height + bar_radius - join_eps;
lip_height_geom = retention_lip_height + join_eps;

bar_tangent_half = max(bar_diameter, end_stop_diameter) / 2;
gusset_span = max(gusset_width, gusset_thickness);
holder_tangent_half = max(bar_tangent_half, gusset_span / 2);
tangent_span_angle = (holder_r > 0)
    ? (holder_tangent_half / holder_r) * 180 / PI
    : 0;

gusset_plate_offsets = (gusset_span > gusset_thickness * 1.5)
    ? [-(gusset_span / 2 - gusset_thickness / 2), (gusset_span / 2 - gusset_thickness / 2)]
    : [0];

if (bar_projection_from_pad_outer > max_projection)
    echo("WARNING: projection exceeds max_projection.");

if (bar_diameter < min_bar_diameter_recommended)
    echo("WARNING: bar_diameter is thin for PETG/PLA wet loads (bar too thin).");
if (gusset_thickness < min_gusset_thickness_recommended)
    echo("WARNING: gusset_thickness is thin for PETG/PLA wet loads (brace too thin).");
if (gusset_height < min_gusset_height_recommended)
    echo("WARNING: gusset_height is low for wet towel load (brace too short).");

if (holder_radial_location_on_pad < 0 || holder_radial_location_on_pad > pad_length)
    echo("WARNING: clamp/pad interference risk: holder_radial_location_on_pad is outside pad_length.");
if (bar_center_height - bar_radius < 0)
    echo("WARNING: clamp/pad interference risk: bar intersects pad plane.");
if (gusset_height > mount_flat_wall_height_available + 0.1)
    echo("WARNING: gusset_height exceeds available clamp flat-wall height.");

if (shared_wall_overlap < 0)
    echo("WARNING: shared_wall_overlap must be >= 0.");
if (shared_wall_overlap > gusset_thickness)
    echo("WARNING: shared_wall_overlap exceeds gusset_thickness.");

if (attach_angle - tangent_span_angle < 0 || attach_angle + tangent_span_angle > sweep_angle)
    echo("WARNING: bar or brace intersects sweep boundaries (tangential span exceeds sweep_angle).");

if (bar_start_local_x < wall_local_x + shared_wall_overlap)
    echo("WARNING: end stops or retention features collide with C-cup wall.");

// -------------------------------
// Clamp / Pad Modules
// -------------------------------
module clamp_profile() {
    polygon(points = profile_points);
}

module pad_profile() {
    pad_x0 = max_profile_x - pad_overlap;
    pad_y0 = max_profile_y - pad_thickness + pad_offset_y;
    translate([pad_x0, pad_y0])
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
// Holder Modules (Local Frame)
// -------------------------------
module holder_bar() {
    if (show_bar) {
        translate([bar_start_local_x_geom, 0, bar_center_height])
            rotate([0, 90, 0])
                cylinder(h = bar_length_geom, r = bar_radius, center = false);
    }

    if (show_end_stop && end_stop_length > 0 && end_stop_diameter > 0) {
        translate([bar_end_local_x - join_eps, 0, bar_center_height])
            rotate([0, 90, 0])
                cylinder(h = end_stop_length + join_eps, r = end_stop_diameter / 2, center = false);
    }

    if (show_retention && retention_lip_height > 0 && retention_lip_width > 0 && lip_length > 0) {
        translate([lip_start_x, -retention_lip_width / 2, lip_start_z])
            cube([lip_length, retention_lip_width, lip_height_geom], center = false);
    }
}

module gusset_plate(y_center) {
    wall_x = wall_local_x - shared_wall_overlap;
    bar_x = bar_start_local_x - gusset_thickness;
    base_h = max(join_eps, pad_thickness);
    top_h = max(join_eps, gusset_height);

    hull() {
        translate([wall_x, y_center - gusset_thickness / 2, 0])
            cube([gusset_thickness + join_eps, gusset_thickness, base_h], center = false);
        translate([bar_x, y_center - gusset_thickness / 2, 0])
            cube([gusset_thickness + join_eps, gusset_thickness, top_h], center = false);
    }
}

module gusset_wall_web() {
    wall_x = wall_local_x - shared_wall_overlap;
    translate([wall_x, -gusset_span / 2, 0])
        cube([gusset_thickness, gusset_span, gusset_height], center = false);
}

module bar_mount_block() {
    block_len = gusset_thickness + join_eps;
    block_h = max(join_eps, min(gusset_height, bar_center_height + bar_radius));
    translate([bar_start_local_x - block_len, -gusset_span / 2, 0])
        cube([block_len, gusset_span, block_h], center = false);
}

module holder_linear() {
    union() {
        holder_bar();
        if (show_gussets) {
            gusset_wall_web();
            for (y = gusset_plate_offsets) gusset_plate(y);
            bar_mount_block();
        }
    }
}

module holder_body() {
    rotate([0, holder_tilt_deg, 0])
        holder_linear();
}

module holder_positioned() {
    attachment_frame(attach_angle, holder_r, holder_profile_y_sweep, 0)
        holder_body();
}

// -------------------------------
// Output
// -------------------------------
if (show_profile) {
    translate([axis_shift_x, 0])
        translate([-axis_x, -axis_z])
            clamp_pad_profile();

    if (show_axis) {
        color("red")
            translate([axis_shift_x, 0])
                circle(r = axis_marker_r, $fn = 48);
    }

    if (show_attach_marker) {
        color("blue")
            translate([holder_origin_x - axis_x + axis_shift_x, holder_profile_y_sweep])
                circle(r = attach_marker_r, $fn = 24);
    }
} else {
    if (render_holder_only) {
        if (show_holder) holder_body();
    } else {
        clamp_pad_sweep();
        if (show_holder) holder_positioned();
    }
}
