// Mid-sweep radial section through full assembly (holder + C-clamp).
// This produces a true cut profile, not a perspective render.

$fn = 40;

use <throwing_water_holder_v2.scad>;

// Current v2 sweep is 24 deg, so midpoint radial cut is 12 deg.
slice_angle_deg = 12;

module full_assembly() {
    clamp_pad_sweep();
    holder_positioned();
}

projection(cut = true)
    rotate([0, slice_angle_deg, 0])
        full_assembly();
