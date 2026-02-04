// Curved tray + hook sweep (Y-axis)
// Uses baked Z=0 profile points for hook and tray

$fn = 200;
include <SpongeHolder_profile_points_cclamp_topref.scad>;
include <SpongeHolder_tray_profile_z0_xy.scad>;

show_profile = false;     // true: show 2D profile only
show_axis = true;
axis_marker_r = 2;

// Sweep parameters
sweep_angle = 45;         // degrees
radius = 222.29;
axis_z = 0;

// Radius reference: "hook_center" or "outer_edge"
radius_ref_mode = "hook_center";

radius_ref_x = (radius_ref_mode == "hook_center") ? hook_center_x : max_profile_x;
axis_x = radius_ref_x - radius;

// Keep rotate_extrude happy (axis left of profile means 0 shift needed)
min_x_all = min(min_profile_x, min_tray_x);
axis_shift_x = max(0, axis_x - min_x_all + 0.1);

module hook_profile() {
    polygon(points=profile_points);
}

module tray_profile() {
    polygon(points=tray_profile_points);
}

// Optional lip around tray (in 2D, swept with tray)
tray_lip_enable = true;
tray_lip_thickness = 1.2;
tray_lip_inset = 0.8;

// End-cap control: remove the end wall from the sweep, then add it back only at start/end.
endcap_enable = true;
endcap_angle = 2;          // degrees; thickness of the cap along the sweep
endcap_side = "right";     // "right" or "left" edge of tray profile
endcap_w = 4;              // width of the end wall slice in 2D

endcap_x = (endcap_side == "right") ? (max_tray_x - endcap_w) : min_tray_x;
endcap_y = min_tray_y;
endcap_h = max_tray_y - min_tray_y;

module endcap_region() {
    translate([endcap_x, endcap_y])
        square([endcap_w, endcap_h]);
}

module tray_lip_profile() {
    difference() {
        offset(r=tray_lip_thickness) tray_profile();
        offset(r=tray_lip_inset) tray_profile();
    }
}

module tray_sweep_profile() {
    // Remove the end wall so it doesn't get swept along the whole arc
    difference() {
        tray_profile();
        if (endcap_enable) endcap_region();
    }
}

module tray_endcap_profile() {
    intersection() {
        tray_profile();
        if (endcap_enable) endcap_region();
    }
}

module combined_profile() {
    translate([axis_shift_x, 0])
        translate([-axis_x, -axis_z])
            union() {
                hook_profile();
                tray_sweep_profile();
                if (tray_lip_enable) tray_lip_profile();
            }
}

if (show_profile) {
    combined_profile();
    if (show_axis) {
        color("red")
            translate([axis_shift_x, 0])
                circle(r=axis_marker_r, $fn=48);
    }
} else {
    // rotate_extrude is around Z; rotate result so axis aligns with Y
    rotate([90,0,0])
        rotate_extrude(angle=sweep_angle)
            combined_profile();

    // Add end caps (wall only at start/end)
    if (endcap_enable) {
        rotate([90,0,0])
            rotate_extrude(angle=endcap_angle)
                translate([axis_shift_x, 0])
                    translate([-axis_x, -axis_z])
                        tray_endcap_profile();

        rotate([90,0,0])
            rotate([0,0,sweep_angle-endcap_angle])
                rotate_extrude(angle=endcap_angle)
                    translate([axis_shift_x, 0])
                        translate([-axis_x, -axis_z])
                            tray_endcap_profile();
    }
}
