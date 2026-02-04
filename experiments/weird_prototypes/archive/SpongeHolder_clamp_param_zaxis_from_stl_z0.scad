// Y-axis sweep using direct STL slice at Z=0 (authoritative)
$fn = 200;

slice_z = 0;
show_profile = true;          // true: render 2D profile, false: 3D swept clamp
show_axis = true;             // show axis marker in 2D profile view
axis_marker_r = 2;

// Optional trim in AXIS space (single keep box)
// This keeps the region left of tray_cut_x and below top_cut_y.
enable_keep = false;
keep_x = -2000;
keep_y = -2000;
keep_w = 1969;                // (-31) - (-2000)
keep_h = 1987;                // (-13) - (-2000)

// Sweep parameters (Y-axis sweep; axis line at X=axis_x, Z=axis_z)
sweep_angle = 120;            // degrees
axis_x = 0;
axis_z = 0;
axis_shift_x = 0;             // shift profile so all X >= 0 for rotate_extrude

module raw_profile() {
    projection(cut=true)
        translate([0,0,-slice_z])
            import("SpongeHolder_export.stl");
}

module clamp_profile() {
    translate([axis_shift_x, 0])
        intersection() {
            translate([-axis_x, -axis_z])
                raw_profile();
            if (enable_keep) {
                translate([keep_x, keep_y])
                    square([keep_w, keep_h]);
            }
        }
}

if (show_profile) {
    clamp_profile();
    if (show_axis) {
        color("red")
            translate([axis_shift_x, 0])
                circle(r=axis_marker_r, $fn=48);
    }
} else {
    // rotate_extrude is around Z; rotate result so axis aligns with Y
    rotate([90,0,0])
        rotate_extrude(angle=sweep_angle)
            clamp_profile();
}
