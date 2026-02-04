// C-clamp only: sweep the trimmed profile around a Y-axis arc

$fn = 200;
include <c_clamp_profile_topref_v1.scad>;

// Display
show_profile = false;   // true = 2D profile only
show_axis = true;
axis_marker_r = 1.5;

// Sweep parameters
sweep_angle = 45;       // degrees
radius = 222.25;        // mm
axis_z = 0;             // Z offset for sweep axis (in profile space)

// Radius reference: "hook_center" or "outer_edge"
radius_ref_mode = "hook_center";
radius_ref_x = (radius_ref_mode == "hook_center") ? hook_center_x : max_profile_x;
axis_x = radius_ref_x - radius;

// Keep rotate_extrude happy (profile must be on +X side)
min_x_all = min_profile_x;
axis_shift_x = max(0, axis_x - min_x_all + 0.1);

module clamp_profile() {
    polygon(points = profile_points);
}

module sweep_profile() {
    translate([axis_shift_x, 0])
        translate([-axis_x, -axis_z])
            clamp_profile();
}

if (show_profile) {
    sweep_profile();
    if (show_axis) {
        color("red")
            translate([axis_shift_x, 0])
                circle(r = axis_marker_r, $fn = 48);
    }
} else {
    // rotate_extrude is around Z; rotate result so axis aligns with Y
    rotate([90, 0, 0])
        rotate_extrude(angle = sweep_angle)
            sweep_profile();
}
