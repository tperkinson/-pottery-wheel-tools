// c_clamp_fit_coupon (v1)
// Clamp-only sweep for fast splash-pan fit testing.

$fn = 200;
include <../../../core_mount_system/c_clamp/v1/c_clamp_profile_topref_v1.scad>;

// -------------------------------
// Quick Tuning (Common)
// -------------------------------
show_profile = false; // true = 2D profile view (no sweep)
show_axis = true;
axis_marker_r = 1.5;

sweep_angle = 30;     // deg (increase to test longer sweep fit)
radius = 222.25;      // mm
radius_ref_mode = "hook_center"; // "hook_center" or "outer_edge"
axis_z = 0;

// Round the outer back-right corner to keep the top connected.
round_outer_corner = true;
outer_corner_radius = 14;            // mm (0 = sharp corner)

// Optional shell to reduce material/time while preserving outer fit surfaces.
shell_thickness =0;                // mm (0 = solid)

// Back-wall windows (reduce mass without breaking sweep continuity).
back_wall_windows = true;
window_depth = 2;                   // mm in from outer wall (X)
window_height = 16;                 // mm (profile Y span)
window_gap = 6;                     // mm between windows (profile Y)
window_count = 2;
window_top_margin = 6;              // mm below top (max_profile_y)
window_bottom_margin = 8;           // mm above bottom (min_profile_y)

// Remove the outer back wall (faster, less rigid).
remove_back_wall = false;
back_wall_cut_depth = 8;            // mm in from outer wall (X)
back_wall_cut_top_margin = 0;       // mm below the back-wall top
back_wall_cut_bottom_margin = 0;    // mm above the back-wall bottom

// -------------------------------
// Derived
// -------------------------------
radius_ref_x = (radius_ref_mode == "hook_center") ? hook_center_x : max_profile_x;
axis_x = radius_ref_x - radius;
axis_shift_x = max(0, axis_x - min_profile_x + 0.1);

corner_cut_x = max_profile_x - outer_corner_radius;
corner_cut_y = max_profile_y - outer_corner_radius;

window_x0 = max_profile_x - window_depth;
window_total_height =
    window_count * window_height + (window_count - 1) * window_gap;
window_available_height =
    (max_profile_y - window_top_margin) - (min_profile_y + window_bottom_margin);

function ys_at_x(points, x, eps = 0.0005) =
    [for (p = points) if (abs(p[0] - x) < eps) p[1]];
back_wall_y_candidates = ys_at_x(profile_points, max_profile_x);
back_wall_min_y = (len(back_wall_y_candidates) > 0) ? min(back_wall_y_candidates) : min_profile_y;
back_wall_max_y = (len(back_wall_y_candidates) > 0) ? max(back_wall_y_candidates) : max_profile_y;
back_wall_cut_x0 = max_profile_x - back_wall_cut_depth;
back_wall_cut_y0 = back_wall_min_y + back_wall_cut_bottom_margin;
back_wall_cut_y1 = back_wall_max_y - back_wall_cut_top_margin;
back_wall_cut_h = back_wall_cut_y1 - back_wall_cut_y0;

if (sweep_angle <= 0)
    echo("WARNING: sweep_angle must be > 0.");
if (radius <= 0)
    echo("WARNING: radius must be > 0.");
if (round_outer_corner && outer_corner_radius < 0)
    echo("WARNING: outer_corner_radius must be >= 0.");
if (round_outer_corner && outer_corner_radius > min(max_profile_x - min_profile_x, max_profile_y - min_profile_y))
    echo("WARNING: outer_corner_radius is too large for the profile bounds.");
if (shell_thickness < 0)
    echo("WARNING: shell_thickness must be >= 0.");
if (back_wall_windows && window_depth <= 0)
    echo("WARNING: window_depth must be > 0 when windows are enabled.");
if (back_wall_windows && window_height <= 0)
    echo("WARNING: window_height must be > 0 when windows are enabled.");
if (back_wall_windows && window_count < 1)
    echo("WARNING: window_count must be >= 1 when windows are enabled.");
if (back_wall_windows && window_total_height > window_available_height)
    echo("WARNING: back-wall windows exceed available height; reduce count/height/gap.");
if (remove_back_wall && back_wall_cut_depth <= 0)
    echo("WARNING: back_wall_cut_depth must be > 0 when remove_back_wall is enabled.");
if (remove_back_wall && back_wall_cut_h <= 0)
    echo("WARNING: back_wall_cut_top/bottom margins remove all back-wall height.");

// -------------------------------
// Core Geometry
// -------------------------------
module clamp_profile_raw() {
    polygon(points = profile_points);
}

module back_wall_window_cut() {
    if (back_wall_windows) {
        for (i = [0 : window_count - 1]) {
            y_top = (max_profile_y - window_top_margin) - i * (window_height + window_gap);
            y_bottom = y_top - window_height;
            translate([window_x0, y_bottom])
                square([window_depth, window_height], center = false);
        }
    }
}

module back_wall_cut() {
    if (remove_back_wall && back_wall_cut_depth > 0 && back_wall_cut_h > 0) {
        translate([back_wall_cut_x0, back_wall_cut_y0])
            square([back_wall_cut_depth, back_wall_cut_h], center = false);
    }
}

module clamp_profile_base() {
    difference() {
        if (!round_outer_corner || outer_corner_radius <= 0) {
            clamp_profile_raw();
        } else {
            difference() {
                clamp_profile_raw();
                // Subtractive fillet only: never adds material.
                translate([corner_cut_x, corner_cut_y])
                    difference() {
                        square([outer_corner_radius, outer_corner_radius], center = false);
                        circle(r = outer_corner_radius, $fn = 64);
                    }
            }
        }
        back_wall_window_cut();
        back_wall_cut();
    }
}

module clamp_profile_coupon() {
    if (shell_thickness <= 0) {
        clamp_profile_base();
    } else {
        difference() {
            clamp_profile_base();
            offset(delta = -shell_thickness)
                clamp_profile_base();
        }
    }
}

module sweep_profile() {
    translate([axis_shift_x, 0])
        translate([-axis_x, -axis_z])
            clamp_profile_coupon();
}

module clamp_sweep() {
    rotate([90, 0, 0])
        rotate_extrude(angle = sweep_angle)
            sweep_profile();
}

// -------------------------------
// Output
// -------------------------------
if (show_profile) {
    sweep_profile();
    if (show_axis) {
        color("red")
            translate([axis_shift_x, 0])
                circle(r = axis_marker_r, $fn = 48);
    }
} else {
    clamp_sweep();
}
