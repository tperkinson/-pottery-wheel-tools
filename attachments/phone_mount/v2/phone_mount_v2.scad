// C-clamp + flat pad (swept) + linear phone holder (not swept)
// Clamp profile is top-referenced (max Y = 0).

$fn = 200;
include <../../../core_mount_system/c_clamp/v1/c_clamp_profile_topref_v1.scad>;

// -------------------------------
// Quick Tuning (Common)
// -------------------------------
render_holder_only = false;  // true = render only holder sample for quick fit tests

show_clamp = true;           // set false to hide clamp body
show_pad = true;             // set false to hide pad
show_holder = true;          // set false to hide holder geometry

auto_sweep_kiss_back_corner = true; // auto size sweep so side planes kiss holder back corners
sweep_angle_manual = 20;     // used when auto_sweep_kiss_back_corner = false
sweep_angle_clearance = 0;   // extra degrees added to auto sweep if desired
radius = 222.25;             // sweep radius (mm)

pad_length = 40;             // platform length (radial)
pad_thickness = 4;           // platform thickness

holder_rest_radial_offset = 20; // holder radial location on pad
holder_top_offset = 0;          // holder vertical offset from profile top
holder_tilt_deg = 20;           // holder tilt around tangent axis
holder_face_center = true;      // true = phone faces inward toward radius center

holder_width = 75;           // holder width (tangent direction)
holder_back_height = 40;     // holder back height
holder_shelf_depth = 26;     // shelf depth
holder_stop_height = 8;      // stop-wall height

// -------------------------------
// Strength / Printability (Common)
// -------------------------------
holder_back_thickness = 4;
holder_shelf_thickness = 4;
holder_stop_thickness = 3;
pad_overlap = 1.0;           // overlap pad into clamp
pad_offset_y = 0;            // keep 0 to preserve top anchor at Y=0
join_eps = 0.05;             // tiny overlap to avoid non-manifold unions

holder_tilt_stilt_enable = true;
holder_tilt_stilt_only_when_tilted = true;
holder_tilt_stilt_width = 60;          // brace width (tangent)
holder_tilt_stilt_inset_from_end = 5;  // pull brace off elevated edge
holder_tilt_stilt_floor_clearance = 0.05; // keep brace above pad plane

// -------------------------------
// Advanced Controls
// -------------------------------
attach_angle_offset = 0;      // additional holder angle tweak after centerline placement
axis_z = 0;                  // profile-space Z offset of sweep axis
radius_ref_mode = "hook_center"; // "hook_center" or "outer_edge"

// Fine transforms in holder-local frame (+X radial, +Y tangent, +Z profile-up).
holder_shift_x = 0;
holder_shift_y = 0;
holder_shift_z = 0;

// Brace detailed shaping.
holder_tilt_stilt_base_offset_x = 0;
holder_tilt_stilt_base_depth = 6;
holder_tilt_stilt_base_height = 2;
holder_tilt_stilt_top_depth = 6;
holder_tilt_stilt_top_height = 9;

// Debug / inspection.
show_profile = false;        // true = 2D clamp+pad profile view
show_axis = true;            // sweep axis marker in profile view
axis_marker_r = 1.5;

show_attach_marker = false;  // marker for holder origin in 2D profile view
attach_marker_r = 1.0;

show_attach_axes = false;    // 3D axes at holder origin
axis_len = 8;
axis_th = 0.6;

// -------------------------------
// Derived
// -------------------------------
radius_ref_x = (radius_ref_mode == "hook_center") ? hook_center_x : max_profile_x;
axis_x = radius_ref_x - radius;
axis_shift_x = max(0, axis_x - min_profile_x + 0.1); // keep profile on +X

holder_attach_x = max_profile_x + holder_rest_radial_offset;
holder_profile_y_2d = max_profile_y + holder_top_offset;
holder_profile_y_sweep = holder_profile_y_2d - axis_z;
holder_r = axis_shift_x + (holder_attach_x - axis_x);
face_sign = holder_face_center ? -1 : 1;

// Auto sweep angle: kiss back-corner width so model can lay flatter on side.
back_corner_x_local = face_sign * holder_back_thickness;
back_corner_x_shifted = back_corner_x_local + holder_shift_x;
back_corner_x_tilted = yrot_x(back_corner_x_shifted, holder_shift_z, holder_tilt_deg);
corner_half_width_y = holder_width / 2 + abs(holder_shift_y);
corner_radius = max(0.001, holder_r + back_corner_x_tilted);
half_kiss_angle = atan2(corner_half_width_y, corner_radius);
sweep_angle_auto = 2 * half_kiss_angle + sweep_angle_clearance;
sweep_angle = auto_sweep_kiss_back_corner ? sweep_angle_auto : sweep_angle_manual;
attach_angle = sweep_angle / 2 + attach_angle_offset;

// Holder clip limits in local attachment frame, relative to sweep boundaries.
clip_angle_min = -attach_angle;
clip_angle_max = sweep_angle - attach_angle;

if (holder_rest_radial_offset < 0 || holder_rest_radial_offset > pad_length)
    echo("WARNING: holder_rest_radial_offset is outside the pad length.");
if (holder_r + back_corner_x_tilted <= 0)
    echo("WARNING: holder corner radius is non-positive; auto sweep may be invalid.");
if (clip_angle_max <= clip_angle_min)
    echo("WARNING: clip angles invalid; holder clip wedge is degenerate.");

function yrot_x(x, z, a_deg) = x * cos(a_deg) + z * sin(a_deg);
function yrot_z(x, z, a_deg) = -x * sin(a_deg) + z * cos(a_deg);

// -------------------------------
// Clamp / Pad Modules
// -------------------------------
module clamp_profile() {
    polygon(points = profile_points);
}

module pad_profile() {
    pad_x0 = max_profile_x - pad_overlap;
    pad_y0 = max_profile_y - pad_thickness + pad_offset_y;
    translate([pad_x0, pad_y0])
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

// -------------------------------
// Attachment Frame / Debug
// -------------------------------
// local +X = radial outward, +Y = tangent, +Z = profile-up
module attachment_frame(angle_deg, radial_r, profile_y, tangent = 0) {
    rotate([90, 0, 0])
        rotate([0, 0, angle_deg])
            translate([radial_r, tangent, profile_y])
                children();
}

module axis_glyph(len = 8, th = 0.6) {
    color("red") cube([len, th, th], center = false);   // +X
    color("green") cube([th, len, th], center = false); // +Y
    color("blue") cube([th, th, len], center = false);  // +Z
}

// -------------------------------
// Holder Modules
// -------------------------------
module holder_linear() {
    face_sign = holder_face_center ? -1 : 1;

    scale([face_sign, 1, 1]) {
        // Back plate: front face at X=0.
        translate([0, -holder_width / 2, 0])
            cube([holder_back_thickness, holder_width, holder_back_height], center = false);

        // Bottom shelf on pad plane (Z=0).
        translate([0, -holder_width / 2, -join_eps])
            cube([holder_shelf_depth, holder_width, holder_shelf_thickness + join_eps], center = false);

        // Front stop wall.
        if (holder_stop_height > 0 && holder_stop_thickness > 0) {
            translate([holder_shelf_depth - holder_stop_thickness, -holder_width / 2, 0])
                cube([holder_stop_thickness, holder_width, holder_stop_height], center = false);
        }
    }
}

module holder_body_transform() {
    rotate([0, holder_tilt_deg, 0])
        translate([holder_shift_x, holder_shift_y, holder_shift_z])
            children();
}

module holder_tilt_stilt() {
    face_sign = holder_face_center ? -1 : 1;
    w = min(holder_tilt_stilt_width, holder_width);
    use_stilt = holder_tilt_stilt_enable &&
                (!holder_tilt_stilt_only_when_tilted || abs(holder_tilt_deg) > 0.01);

    if (use_stilt) {
        // Determine which shelf end is elevated after tilt.
        x_near = holder_shift_x;
        x_far = holder_shift_x + face_sign * holder_shelf_depth;
        z_near = yrot_z(x_near, holder_shift_z, holder_tilt_deg);
        z_far = yrot_z(x_far, holder_shift_z, holder_tilt_deg);
        x_end_local = (z_far >= z_near) ? (face_sign * holder_shelf_depth) : 0;

        // Anchor the brace near elevated edge, inset slightly inboard.
        x_anchor_local = x_end_local - face_sign * holder_tilt_stilt_inset_from_end;
        x_anchor_shifted = x_anchor_local + holder_shift_x;
        x_anchor = yrot_x(x_anchor_shifted, holder_shift_z, holder_tilt_deg);
        z_anchor = yrot_z(x_anchor_shifted, holder_shift_z, holder_tilt_deg);

        // Keep brace feet at/above pad plane (Z >= floor_clearance).
        base_center_x = x_anchor + holder_tilt_stilt_base_offset_x;
        base_x0 = base_center_x - holder_tilt_stilt_base_depth / 2;
        base_y0 = holder_shift_y - w / 2;
        base_z0 = holder_tilt_stilt_floor_clearance;

        top_x0 = x_anchor - holder_tilt_stilt_top_depth / 2;
        top_y0 = holder_shift_y - w / 2;
        top_z0 = max(holder_tilt_stilt_floor_clearance, z_anchor - holder_tilt_stilt_top_height);

        hull() {
            translate([base_x0, base_y0, base_z0])
                cube([holder_tilt_stilt_base_depth, w, holder_tilt_stilt_base_height], center = false);
            translate([top_x0, top_y0, top_z0])
                cube([holder_tilt_stilt_top_depth, w, holder_tilt_stilt_top_height], center = false);
        }
    }
}

module holder_assembly_local() {
    union() {
        holder_tilt_stilt();
        holder_body_transform()
            holder_linear();
    }
}

module holder_sweep_clip_local() {
    // Infinite-ish wedge in local XY around the sweep axis at X=-holder_r.
    // Intersection of this wedge with holder geometry trims both side edges
    // to the same angular limits used by the sweep.
    clip_origin_x = -holder_r;
    clip_len = holder_r + max(pad_length, holder_shelf_depth) + 200;
    clip_half_z = max(holder_back_height + abs(holder_shift_z) + 50, 120);

    p0 = [clip_origin_x, 0];
    p1 = [clip_origin_x + clip_len * cos(clip_angle_min), clip_len * sin(clip_angle_min)];
    p2 = [clip_origin_x + clip_len * cos(clip_angle_max), clip_len * sin(clip_angle_max)];

    linear_extrude(height = 2 * clip_half_z, center = true)
        polygon(points = [p0, p1, p2]);
}

module holder_clipped_to_sweep_local() {
    intersection() {
        holder_sweep_clip_local();
        holder_assembly_local();
    }
}

module holder_positioned() {
    attachment_frame(attach_angle, holder_r, holder_profile_y_sweep, 0)
        holder_clipped_to_sweep_local();
}

module holder_only_sample() {
    // Holder-only preview/print sample in local frame for fast test prints.
    holder_clipped_to_sweep_local();
}

// -------------------------------
// Output
// -------------------------------
if (show_profile) {
    // 2D view shows clamp + pad only.
    translate([axis_shift_x, 0])
        translate([-axis_x, -axis_z])
            clamp_pad_profile();

    if (show_attach_marker) {
        color("orange")
            translate([axis_shift_x, 0])
                translate([-axis_x, -axis_z])
                    translate([holder_attach_x, holder_profile_y_2d])
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
        if (show_attach_axes)
            axis_glyph(axis_len, axis_th);
    } else {
        union() {
            clamp_pad_sweep();
            if (show_holder) holder_positioned();
        }

        if (show_attach_axes) {
            attachment_frame(attach_angle, holder_r, holder_profile_y_sweep, 0)
                axis_glyph(axis_len, axis_th);
        }
    }
}
