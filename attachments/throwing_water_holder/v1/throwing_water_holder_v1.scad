// throwing_water_holder (v1)
// Reset baseline: open-top rounded box holder on canonical C-clamp sweep.

$fn = 96;
include <../../../core_mount_system/c_clamp/v1/c_clamp_profile_topref_v1.scad>;

// -------------------------------
// Quick Tuning
// -------------------------------
render_holder_only = false;      // true = render holder-only sample
holder_only_side_print = false;  // true = rotate holder-only sample onto its side

show_clamp = true;
show_pad = false;
show_holder = true;

radius = 222.25;                 // mm
radius_ref_mode = "hook_center"; // "hook_center" or "outer_edge"
axis_z = 0;

sweep_angle = 24;                // deg
pad_length = 8;                  // mm
pad_thickness = 4;               // mm
pad_overlap = 1.0;               // mm
pad_offset_y = 0;                // keep 0 to preserve top reference

holder_top_offset = 16;          // mm (top rim relative to clamp top)
holder_tilt_deg = 2;             // deg (drain toward clamp side)
holder_angle_offset = 0;         // deg
holder_radial_location_on_pad = 0; // mm from clamp wall to box inner wall
shared_wall_overlap = 1.5;       // mm merge into clamp wall

// Open-top rounded box
box_width = 112;                 // mm radial size
box_length = 118;                // mm tangent size
box_depth = 64;                  // mm below top rim
wall_thickness = 3.6;            // mm
floor_thickness = 4.5;           // mm
seam_radius = 6;                 // mm rounds exterior/interior seams

// Build envelope
max_projection = 127;            // mm from pad outer edge
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
attach_angle = sweep_angle / 2 + holder_angle_offset;

box_x0 = -shared_wall_overlap;
box_x1 = box_x0 + box_width;
box_y0 = -box_length / 2;
box_z0 = -box_depth;

inner_w = box_width - 2 * wall_thickness;
inner_l = box_length - 2 * wall_thickness;
inner_h = box_depth - floor_thickness;

pad_outer_local_x = pad_length - holder_radial_location_on_pad;
projection_from_pad_outer = box_x1 - pad_outer_local_x;

volume_ml_est = (inner_w > 0 && inner_l > 0 && inner_h > 0)
    ? (inner_w * inner_l * inner_h) / 1000
    : 0;

echo(str("INFO: volume estimate (ml) = ", volume_ml_est));

if (wall_thickness < 3.0)
    echo("WARNING: wall_thickness < 3.0 mm may be weak.");
if (floor_thickness < 3.8)
    echo("WARNING: floor_thickness < 3.8 mm may be weak.");
if (inner_w <= 0 || inner_l <= 0 || inner_h <= 0)
    echo("WARNING: invalid box dimensions (inner cavity collapsed).");
if (holder_radial_location_on_pad < 0 || holder_radial_location_on_pad > pad_length)
    echo("WARNING: holder_radial_location_on_pad is outside pad_length.");
if (projection_from_pad_outer > max_projection)
    echo("WARNING: projection exceeds max_projection.");
if (box_width > ender3_v3_bed_x || box_length > ender3_v3_bed_y)
    echo("WARNING: holder-only footprint likely exceeds Ender 3 V3 bed (220x220 mm).");

// -------------------------------
// Helpers
// -------------------------------
module rounded_box(size = [10, 10, 10], r = 0) {
    rr = min(r, min(size[0], min(size[1], size[2])) / 2 - 0.01);

    if (rr > 0) {
        minkowski() {
            cube([size[0] - 2 * rr, size[1] - 2 * rr, size[2] - 2 * rr], center = false);
            sphere(r = rr);
        }
    } else {
        cube(size, center = false);
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

// local +X = radial outward, +Y = tangent, +Z = profile-up
module attachment_frame(angle_deg, radial_r, profile_y, tangent = 0) {
    rotate([90, 0, 0])
        rotate([0, 0, angle_deg])
            translate([radial_r, tangent, profile_y])
                children();
}

// -------------------------------
// Holder Geometry (linear)
// -------------------------------
module holder_linear() {
    inner_r = max(0, min(seam_radius, wall_thickness - 0.2));

    difference() {
        translate([box_x0, box_y0, box_z0])
            rounded_box([box_width, box_length, box_depth], seam_radius);

        translate([box_x0 + wall_thickness, box_y0 + wall_thickness, box_z0 + floor_thickness])
            rounded_box([
                box_width - 2 * wall_thickness,
                box_length - 2 * wall_thickness,
                box_depth - floor_thickness + 1.0
            ], inner_r);
    }
}

module holder_local_placed() {
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
