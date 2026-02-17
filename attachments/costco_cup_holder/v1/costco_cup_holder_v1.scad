// costco_cup_holder (v1)
// Lip-capture hoop for a Solo-style cup using the canonical C-clamp mount.

$fn = 180;
include <../../../core_mount_system/c_clamp/v1/c_clamp_profile_topref_v1.scad>;

// -------------------------------
// Quick Tuning (Common)
// -------------------------------
render_holder_only = true; // true = quick sample print of holder only

show_clamp = true;
show_pad = true;
show_holder = true;

sweep_angle = 24;                // deg, manual fallback
sweep_fit_mode = "auto_hoop_kiss"; // "manual" or "auto_hoop_kiss"
sweep_fit_diameter_mode = "hoop_outer"; // "hoop_outer" or "cup_lip_exterior"
sweep_kiss_clearance = 0.0;      // extra radial margin for sweep-fit calc

radius = 222.25;                 // mm
radius_ref_mode = "hook_center"; // "hook_center" or "outer_edge"
axis_z = 0;

pad_length = 13.5;
pad_thickness = 5;
pad_overlap = 1.0;
pad_offset_y = 0;                // keep 0 to preserve top-reference behavior

// Cup / hoop fit
cup_lip_diameter = 97.0;          // measured OD at rolled lip
cup_body_diameter_below_lip = 93.5; // OD just below lip where cup passes through
ring_thickness = 5.5;             // radial hoop wall thickness
clearance = 0.35;                 // added to body pass-through diameter
ring_height = 5; // use 14 for final, 5 just to check;                 // vertical hoop height for lip support

// Holder placement
attach_angle = sweep_angle / 2;   // used when attach_angle_mode = "manual"
attach_angle_mode = "auto_center"; // "auto_center" or "manual"
holder_radial_location_on_pad = pad_length * 0.25;
holder_top_offset = 0;
holder_tilt_deg = 5;

// Bridge and strength
hoop_center_offset_from_mount = 60; // targets ~10 mm gap from pad outer edge to ring start
bridge_width = 40;
bridge_thickness = 4;
bridge_overlap_into_ring = 1;

enable_mount_gusset = true;
mount_gusset_width = 2300;
mount_gusset_mount_inset = 3;
mount_gusset_ring_inset = 0;
mount_gusset_base_depth = 8;
mount_gusset_base_height = 3;
mount_gusset_top_depth = 3;
mount_gusset_top_height = 10;

// -------------------------------
// Advanced Controls
// -------------------------------
show_profile = false;
show_axis = true;
axis_marker_r = 1.5;

show_attach_marker = false;
attach_marker_r = 1.0;

// -------------------------------
// Derived
// -------------------------------
radius_ref_x = (radius_ref_mode == "hook_center") ? hook_center_x : max_profile_x;
axis_x = radius_ref_x - radius;
axis_shift_x = max(0, axis_x - min_profile_x + 0.1);

attach_x = max_profile_x + holder_radial_location_on_pad;
attach_profile_y_2d = max_profile_y + holder_top_offset;
attach_profile_y_sweep = attach_profile_y_2d - axis_z;
attach_r = axis_shift_x + (attach_x - axis_x);

hoop_inner_diameter = cup_body_diameter_below_lip + (2 * clearance);
hoop_outer_diameter = hoop_inner_diameter + (2 * ring_thickness);
hoop_outer_radius = hoop_outer_diameter / 2;
lip_seat_radial_margin = (cup_lip_diameter - hoop_inner_diameter) / 2;

hoop_center_radial_for_sweep = attach_r + (hoop_center_offset_from_mount * cos(holder_tilt_deg));
sweep_fit_radius = (((sweep_fit_diameter_mode == "cup_lip_exterior") ? cup_lip_diameter : hoop_outer_diameter) / 2) + sweep_kiss_clearance;
sweep_half_angle_auto = (hoop_center_radial_for_sweep > 0) ? asin(min(1, sweep_fit_radius / hoop_center_radial_for_sweep)) : 90;
sweep_angle_auto = 2 * sweep_half_angle_auto;
sweep_angle_effective = (sweep_fit_mode == "auto_hoop_kiss") ? sweep_angle_auto : sweep_angle;
attach_angle_effective = (attach_angle_mode == "auto_center") ? (sweep_angle_effective / 2) : attach_angle;

bridge_length = max(0.1, hoop_center_offset_from_mount - hoop_outer_radius + bridge_overlap_into_ring);

// "Under-hoop open" check: hole should begin beyond pad outer edge.
pad_outer_x_from_mount = pad_length - holder_radial_location_on_pad;
hole_min_x_from_mount = hoop_center_offset_from_mount - (hoop_inner_diameter / 2);
under_hoop_open_margin = 2.0;

if (holder_radial_location_on_pad < 0 || holder_radial_location_on_pad > pad_length)
    echo("WARNING: holder_radial_location_on_pad is outside pad_length.");

if (lip_seat_radial_margin <= 0)
    echo("WARNING: cup lip will not seat. Increase cup_lip_diameter or reduce hole diameter.");

if (ring_thickness < 3)
    echo("WARNING: ring_thickness < 3 mm may be weak for loaded cup.");

if (bridge_length <= 0.5)
    echo("WARNING: hoop center is too close to mount; bridge has near-zero length.");

if (hole_min_x_from_mount <= pad_outer_x_from_mount + under_hoop_open_margin)
    echo("WARNING: hole overlaps pad under the hoop. Increase hoop_center_offset_from_mount and/or holder_radial_location_on_pad.");

if (sweep_fit_mode == "auto_hoop_kiss" && hoop_center_radial_for_sweep <= sweep_fit_radius)
    echo("WARNING: auto sweep-fit invalid; sweep-fit radius exceeds hoop center radius.");

// -------------------------------
// Clamp / Pad Geometry (swept)
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
        rotate_extrude(angle = sweep_angle_effective)
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
// Holder Geometry (linear, non-swept)
// -------------------------------
module holder_hoop_linear() {
    difference() {
        cylinder(h = ring_height, d = hoop_outer_diameter, center = false);
        translate([0, 0, -0.1])
            cylinder(h = ring_height + 0.2, d = hoop_inner_diameter, center = false);
    }
}

module holder_bridge_linear() {
    translate([0, -bridge_width / 2, 0])
        cube([bridge_length, bridge_width, bridge_thickness], center = false);
}

module holder_mount_gusset_linear() {
    if (enable_mount_gusset) {
        gusset_width_eff = min(mount_gusset_width, bridge_width);
        x_base = max(0, mount_gusset_mount_inset);
        x_top = max(x_base + 0.1, hoop_center_offset_from_mount - hoop_outer_radius + mount_gusset_ring_inset);
        y0 = -gusset_width_eff / 2;
        z_top = max(bridge_thickness, ring_height - mount_gusset_top_height);

        hull() {
            translate([x_base, y0, 0])
                cube([mount_gusset_base_depth, gusset_width_eff, mount_gusset_base_height], center = false);
            translate([x_top, y0, z_top])
                cube([mount_gusset_top_depth, gusset_width_eff, mount_gusset_top_height], center = false);
        }
    }
}

module holder_linear() {
    union() {
        holder_bridge_linear();
        holder_mount_gusset_linear();
        translate([hoop_center_offset_from_mount, 0, 0])
            holder_hoop_linear();
    }
}

module holder_positioned() {
    attachment_frame(attach_angle_effective, attach_r, attach_profile_y_sweep, 0)
        rotate([0, holder_tilt_deg, 0])
            holder_linear();
}

module holder_only_sample() {
    holder_linear();
}

// -------------------------------
// Output
// -------------------------------
if (show_profile) {
    translate([axis_shift_x, 0])
        translate([-axis_x, -axis_z])
            clamp_pad_profile();

    if (show_attach_marker) {
        color("orange")
            translate([axis_shift_x, 0])
                translate([-axis_x, -axis_z])
                    translate([attach_x, attach_profile_y_2d])
                        circle(r = attach_marker_r, $fn = 36);
    }

    if (show_axis) {
        color("red")
            translate([axis_shift_x, 0])
                circle(r = axis_marker_r, $fn = 48);
    }
} else {
    if (render_holder_only) {
        if (show_holder) holder_only_sample();
    } else {
        union() {
            clamp_pad_sweep();
            if (show_holder) holder_positioned();
        }
    }
}
