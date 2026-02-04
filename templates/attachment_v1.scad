// __ATTACHMENT_NAME__ (__VERSION__)
// Starter template using the canonical C-clamp profile.

$fn = 180;
include <../../../core_mount_system/c_clamp/v1/c_clamp_profile_topref_v1.scad>;

// -------------------------------
// Quick Tuning (Common)
// -------------------------------
render_holder_only = false; // true = quick sample print of attachment only

show_clamp = true;
show_pad = true;
show_attachment = true;

sweep_angle = 24;           // deg
radius = 222.25;            // mm
radius_ref_mode = "hook_center"; // "hook_center" or "outer_edge"
axis_z = 0;

pad_length = 36;
pad_thickness = 4;
pad_overlap = 1.0;

attach_angle = sweep_angle / 2;
attachment_radial_offset = pad_length * 0.5;
attachment_top_offset = 0;
attachment_tilt_deg = 0;

attachment_width = 30;      // tangent direction
attachment_height = 35;     // profile-up
attachment_depth = 12;      // radial

// -------------------------------
// Advanced Controls
// -------------------------------
show_profile = false;
show_axis = true;
axis_marker_r = 1.5;

// -------------------------------
// Derived
// -------------------------------
radius_ref_x = (radius_ref_mode == "hook_center") ? hook_center_x : max_profile_x;
axis_x = radius_ref_x - radius;
axis_shift_x = max(0, axis_x - min_profile_x + 0.1);

attach_x = max_profile_x + attachment_radial_offset;
attach_profile_y_2d = max_profile_y + attachment_top_offset;
attach_profile_y_sweep = attach_profile_y_2d - axis_z;
attach_r = axis_shift_x + (attach_x - axis_x);

if (attachment_radial_offset < 0 || attachment_radial_offset > pad_length)
    echo("WARNING: attachment_radial_offset is outside pad_length.");

// -------------------------------
// Core Geometry
// -------------------------------
module clamp_profile() {
    polygon(points = profile_points);
}

module pad_profile() {
    x0 = max_profile_x - pad_overlap;
    y0 = max_profile_y - pad_thickness;
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

module attachment_linear() {
    translate([0, -attachment_width / 2, 0])
        cube([attachment_depth, attachment_width, attachment_height], center = false);
}

module attachment_positioned() {
    attachment_frame(attach_angle, attach_r, attach_profile_y_sweep, 0)
        rotate([0, attachment_tilt_deg, 0])
            attachment_linear();
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
} else {
    if (render_holder_only) {
        if (show_attachment) attachment_linear();
    } else {
        clamp_pad_sweep();
        if (show_attachment) attachment_positioned();
    }
}
