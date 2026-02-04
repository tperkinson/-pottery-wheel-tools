// Parametric curved tray + hook sweep (Y-axis)
// Hook profile from Z=0 slice (keep-box baked)

$fn = 200;
include <../../../core_mount_system/c_clamp/v1/c_clamp_profile_topref_v1.scad>;

// Display
show_profile = false;     // true: show 2D profile only
show_axis = true;
axis_marker_r = 2;

// Sweep parameters
sweep_angle = 30;         // degrees
radius = 222.29;          // mm
axis_z = 0;

// Radius reference: "hook_center" or "outer_edge"
radius_ref_mode = "hook_center";

radius_ref_x = (radius_ref_mode == "hook_center") ? hook_center_x : max_profile_x;
axis_x = radius_ref_x - radius;

// Keep rotate_extrude happy
min_x_all = min_profile_x; // hook profile already shifted so min X = 0
axis_shift_x = max(0, axis_x - min_x_all + 0.1);

// Tray parameters (inches)
inch = 25.4;
tray_radial_len = 6 * inch;           // radial length
tray_thickness = 3/16 * inch;         // base thickness
inner_wall_height = 3/16 * inch;
inner_wall_thickness = 3/16 * inch;
outer_wall_height = 1/2 * inch;
outer_wall_thickness = 3/16 * inch;

// End walls at sweep start/end
sidewall_height = 1/2 * inch;
sidewall_thickness = 3/16 * inch;     // along sweep direction

// Tray tilt (positive lifts the outer edge)
tray_tilt_deg = 5;

// Tray placement relative to hook
// Attach at the top sharp corner of the hook profile.
// Offset by tray_thickness so the full tray thickness mates with the hook.
tray_attach_x = max_profile_x;        // hook outer edge
tray_attach_y = max_profile_y - tray_thickness;  // seat tray onto hook

module hook_profile() {
    polygon(points=profile_points);
}

module tray_profile_2d() {
    // Base plate
    square([tray_radial_len, tray_thickness], center=false);
    // Inner wall (near hook)
    square([inner_wall_thickness, inner_wall_height], center=false);
    // Outer wall
    translate([tray_radial_len - outer_wall_thickness, 0])
        square([outer_wall_thickness, outer_wall_height], center=false);
}

module tray_profile_tilted() {
    translate([tray_attach_x, tray_attach_y])
        rotate(tray_tilt_deg)
            tray_profile_2d();
}

module sidewall_profile_tilted() {
    translate([tray_attach_x, tray_attach_y])
        rotate(tray_tilt_deg)
            square([tray_radial_len, sidewall_height], center=false);
}

module combined_profile() {
    translate([axis_shift_x, 0])
        translate([-axis_x, -axis_z])
            union() {
                hook_profile();
                tray_profile_tilted();
            }
}

module endcap_profile() {
    translate([axis_shift_x, 0])
        translate([-axis_x, -axis_z])
            sidewall_profile_tilted();
}

if (show_profile) {
    combined_profile();
    if (show_axis) {
        color("red")
            translate([axis_shift_x, 0])
                circle(r=axis_marker_r, $fn=48);
    }
} else {
    // Sweep tray + hook
    rotate([90,0,0])
        rotate_extrude(angle=sweep_angle)
            combined_profile();

    // Add end walls (caps) at sweep start/end
    cap_angle = (sidewall_thickness / radius) * 180 / PI;

    rotate([90,0,0])
        rotate_extrude(angle=cap_angle)
            endcap_profile();

    rotate([90,0,0])
        rotate([0,0,sweep_angle-cap_angle])
            rotate_extrude(angle=cap_angle)
                endcap_profile();
}
