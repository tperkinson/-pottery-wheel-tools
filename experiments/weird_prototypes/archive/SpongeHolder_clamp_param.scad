// Parametric rebuild of SpongeHolder clamp from STL slice
// Step 1: Extract 2D profile (Z-slice) and trim tray

slice_z = 93.340206;          // Z slice height (from STL mid-plane)
show_profile = true;          // true: render 2D profile, false: 3D swept clamp
show_axis = true;             // show axis marker in 2D profile view
axis_marker_r = 2;

// Tray removal (adjust to trim the flat tray) - coordinates are in AXIS space
tray_cut_x = 12.972;             // everything to the right of this gets removed
tray_cut_y = -154.218;
tray_cut_w = 2000;
tray_cut_h = 2000;

// Top removal (adjust to trim any remaining tray at the top of the C-cup) - AXIS space
enable_top_cut = true;
top_cut_y = 30.482;          // everything above this gets removed
top_cut_x = -1937.328;
top_cut_w = 4000;
top_cut_h = 2000;

// Sweep parameters
sweep_angle = 120;            // degrees
axis_x = -62.672;             // estimated axis center X (auto)
axis_y = -45.782;             // estimated axis center Y (auto)
axis_shift_x = 15.014;        // shift profile so all X >= 0 for rotate_extrude

module raw_profile() {
    projection(cut=true)
        translate([0,0,-slice_z])
            import("SpongeHolder_export.stl");
}

module clamp_profile() {
    // Move profile so the sweep axis is at the origin.
    // Cuts are defined in this axis-centered space for easier tuning.
    translate([axis_shift_x, 0])
        difference() {
            translate([-axis_x, -axis_y])
                raw_profile();
            translate([tray_cut_x, tray_cut_y])
                square([tray_cut_w, tray_cut_h]);
            if (enable_top_cut) {
                translate([top_cut_x, top_cut_y])
                    square([top_cut_w, top_cut_h]);
            }
        }
}

if (show_profile) {
    clamp_profile();
    if (show_axis) {
        color("red")
            translate([0,0])
                circle(r=axis_marker_r, $fn=48);
    }
} else {
    rotate_extrude(angle=sweep_angle)
        clamp_profile();
}
