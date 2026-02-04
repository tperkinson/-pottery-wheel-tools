// throwing_water_holder (v1)
// Open throwing-water basin using canonical C-clamp/C-cup sweep.
// Design intent: low profile, shared mount wall, high capacity from footprint.

$fn = 180;
include <../../../core_mount_system/c_clamp/v1/c_clamp_profile_topref_v1.scad>;

// -------------------------------
// Quick Tuning (Common)
// -------------------------------
render_holder_only = false;                  // true = quick holder-only sample print
holder_only_with_shared_wall_proxy = true;   // visualize shared-wall contact in holder-only mode
holder_only_side_print = false;              // rotate holder-only sample onto its side for printing
holder_only_side_print_match_sweep = true;   // align sweep edge to bed before side-rotation
holder_only_side_print_edge = "start";       // "start" or "end" sweep edge to lay down
holder_only_side_print_x_deg = 90;           // side-rotation about X axis (use -90 for opposite)

show_clamp = true;
show_pad = false;
show_holder = true;
show_holder_shell = true;
show_holder_side_walls = true;

radius = 222.25;                            // mm
radius_ref_mode = "hook_center";            // "hook_center" or "outer_edge"
axis_z = 0;

pad_length = 8;
pad_thickness = 4;
pad_overlap = 1.0;
pad_offset_y = 0;                           // keep 0 for top-reference behavior

// Capacity targets
target_volume_ml = 946;                     // 32 oz fill-line target
volume_headroom_ml = 105;                   // desired extra volume above fill line

// Basin footprint and depth
arc_length = 172.3;                         // mm centerline arc length
radial_width = 110;                         // mm overall radial body width
depth = 58;                                 // mm interior depth at back wall
wall_thickness = 3.6;
floor_thickness = 4.5;

holder_tilt_deg = 2;
holder_radial_location_on_pad = radial_width / 2;
holder_top_offset = 6.5;                    // back-rim top relative to clamp top
holder_angle_offset = 0;

// Slosh behavior (back wall taller than front wall)
front_wall_height = depth + floor_thickness - 6;
back_wall_height = depth + floor_thickness;

// Shared-wall and cleaning controls
shared_wall_overlap = 1.8;                  // radial merge strip into mount wall
shared_wall_blend_radius = 3.0;             // local front-corner thickening
interior_corner_radius = 4.0;               // floor-to-wall interior blend helper
front_rim_round_radius = 3.0;               // round top inner edge of front/shared wall (basin side)
// Optional feature toggles
enable_shared_wall_blend = true;
enable_interior_floor_blend = true;
enable_front_rim_round = true;

// Sweep envelope around holder
match_sweep_to_holder = true;               // true = sweep angle matches holder arc
sweep_side_margin_deg = 4.0;                // extra sweep margin when match_sweep_to_holder = false

// Heavy-load reinforcement (external end gussets)
enable_mount_gussets = true;
mount_gusset_tangent_width = 7;
mount_gusset_base_depth = 13;
mount_gusset_base_height = 5;
mount_gusset_top_depth = 10;
mount_gusset_top_height = 18;

// -------------------------------
// Advanced Controls / Debug
// -------------------------------
show_profile = false;
show_axis = true;
show_attach_marker = false;
axis_marker_r = 1.5;
attach_marker_r = 1.0;

mount_flat_wall_height_nominal = 45.4;      // nominal flat-wall span seen in profile
max_recommended_overlap = 4.0;
join_eps = 0.05;

ender3_v3_bed_x = 220;
ender3_v3_bed_y = 220;

// -------------------------------
// Derived
// -------------------------------
radius_ref_x = (radius_ref_mode == "hook_center") ? hook_center_x : max_profile_x;
axis_x = radius_ref_x - radius;
axis_shift_x = max(0, axis_x - min_profile_x + 0.1);

shared_wall_attach_x = max_profile_x;
shared_wall_top_profile_y_2d = max_profile_y + holder_top_offset;
shared_wall_top_profile_y_sweep = shared_wall_top_profile_y_2d - axis_z;
shared_wall_radius = axis_shift_x + (shared_wall_attach_x - axis_x);

centerline_radius = shared_wall_radius + holder_radial_location_on_pad;
arc_angle_deg = (centerline_radius > 0) ? (arc_length / centerline_radius) * 180 / PI : 0;

sweep_side_margin_deg_effective = match_sweep_to_holder ? 0 : sweep_side_margin_deg;
sweep_angle_effective = arc_angle_deg + 2 * sweep_side_margin_deg_effective;
attach_angle_effective = sweep_side_margin_deg_effective + arc_angle_deg / 2 + holder_angle_offset;

inner_radius = centerline_radius - radial_width / 2;
outer_radius = centerline_radius + radial_width / 2;

body_inner_radius = inner_radius - shared_wall_overlap;
body_outer_radius = outer_radius;
cavity_inner_radius = inner_radius;
cavity_outer_radius = outer_radius - wall_thickness;

a_start = -arc_angle_deg / 2;
a_end = arc_angle_deg / 2;
holder_start_angle = attach_angle_effective + a_start;
holder_end_angle = attach_angle_effective + a_end;

cavity_ref_radius = max(1, (cavity_inner_radius + cavity_outer_radius) / 2);
end_wall_angle_thickness = (cavity_ref_radius > 0) ? (wall_thickness / cavity_ref_radius) * 180 / PI : 0;

interior_plan_area_mm2 = 0.5 * (arc_angle_deg * PI / 180)
    * max(0, cavity_outer_radius * cavity_outer_radius - cavity_inner_radius * cavity_inner_radius);

fill_line_height = max(0, front_wall_height - floor_thickness);
full_height = max(0, back_wall_height - floor_thickness);

fill_line_volume_ml_est = interior_plan_area_mm2 * fill_line_height / 1000;
max_volume_ml_est = interior_plan_area_mm2 * full_height / 1000;
headroom_ml_est = max(0, max_volume_ml_est - fill_line_volume_ml_est);

mount_gusset_span_deg = (centerline_radius > 0)
    ? (mount_gusset_tangent_width / centerline_radius) * 180 / PI
    : 0;

footprint_half_angle = min(
    89.5,
    max(
        0,
        arc_angle_deg / 2 + (enable_mount_gussets ? mount_gusset_span_deg : 0)
    )
);

footprint_x_min = -shared_wall_radius + body_inner_radius * cos(footprint_half_angle);
footprint_x_max = -shared_wall_radius + body_outer_radius;
holder_footprint_x = footprint_x_max - footprint_x_min;
holder_footprint_y = 2 * body_outer_radius * sin(footprint_half_angle);

echo(str("INFO: fill-line volume estimate (ml) = ", fill_line_volume_ml_est));
echo(str("INFO: max-to-back-rim volume estimate (ml) = ", max_volume_ml_est));
echo(str("INFO: estimated volume headroom (ml) = ", headroom_ml_est));
echo(str("INFO: holder-only footprint estimate (mm) = ", holder_footprint_x, " x ", holder_footprint_y));

if (fill_line_volume_ml_est < target_volume_ml)
    echo("WARNING: fill-line volume estimate is below target_volume_ml.");
if (headroom_ml_est < volume_headroom_ml)
    echo("WARNING: estimated volume headroom is below volume_headroom_ml.");

if (depth < 50 || depth > 65)
    echo("WARNING: depth is outside preferred low-profile band (50-65 mm).");
if (wall_thickness < 3.0)
    echo("WARNING: wall_thickness < 3.0 mm may be weak in PETG for wet load.");
if (floor_thickness < 3.8)
    echo("WARNING: floor_thickness < 3.8 mm may be weak in PETG for wet load.");
if (shared_wall_overlap < 1.2)
    echo("WARNING: shared_wall_overlap < 1.2 mm may be weak for shared-wall load transfer.");
if (shared_wall_overlap > max_recommended_overlap)
    echo("WARNING: shared_wall_overlap is larger than recommended.");
if (interior_corner_radius < 2.0)
    echo("WARNING: interior_corner_radius < 2.0 mm reduces cleanability.");
if (enable_front_rim_round && front_rim_round_radius > 0 && front_rim_round_radius < 1.5)
    echo("WARNING: front_rim_round_radius < 1.5 mm may still feel sharp.");
if (enable_front_rim_round && front_rim_round_radius > 0 && front_rim_round_radius > (front_wall_height - floor_thickness))
    echo("WARNING: front_rim_round_radius exceeds front wall height; reduce radius.");
if (enable_front_rim_round && front_rim_round_radius > 0 && front_rim_round_radius > cavity_inner_radius)
    echo("WARNING: front_rim_round_radius exceeds cavity inner radius; reduce radius.");

if (enable_mount_gussets && (
    mount_gusset_tangent_width < 6
    || mount_gusset_base_depth < 8
    || mount_gusset_base_height < 3
    || mount_gusset_top_depth < 6
    || mount_gusset_top_height < 10
))
    echo("WARNING: gusset dimensions are thin for heavy-load handling shock.");

if (arc_length <= 0 || radial_width <= 0 || depth <= 0)
    echo("WARNING: arc_length, radial_width, and depth must all be > 0.");
if (front_wall_height <= floor_thickness)
    echo("WARNING: front_wall_height must exceed floor_thickness.");
if (back_wall_height <= floor_thickness)
    echo("WARNING: back_wall_height must exceed floor_thickness.");
if (back_wall_height <= front_wall_height)
    echo("WARNING: back_wall_height should be > front_wall_height for slosh control.");
if (centerline_radius <= 0 || inner_radius <= 0 || outer_radius <= inner_radius || arc_angle_deg <= 0)
    echo("WARNING: invalid annular-sector dimensions; check radii/arc inputs.");
if (arc_angle_deg >= 170)
    echo("WARNING: arc angle is too large and may self-intersect or be hard to print.");
if (cavity_outer_radius <= cavity_inner_radius)
    echo("WARNING: radial_width too small for requested wall_thickness.");
if (body_inner_radius <= 0)
    echo("WARNING: shared_wall_overlap pushes body across sweep axis.");

if (abs(inner_radius - shared_wall_radius) > 0.6)
    echo("WARNING: holder_radial_location_on_pad no longer aligns cavity front with shared mount wall.");
if (match_sweep_to_holder && abs(holder_angle_offset) > 0.1)
    echo("WARNING: holder_angle_offset prevents sweep/holder edge alignment.");
if (holder_start_angle < 0 || holder_end_angle > sweep_angle_effective)
    echo("WARNING: holder envelope exceeds clamp/pad sweep limits.");
if (show_pad && pad_length > holder_radial_location_on_pad + wall_thickness)
    echo("WARNING: pad overhang may block top access near shared wall.");
if (holder_top_offset - back_wall_height < min_profile_y + 2)
    echo("WARNING: holder depth reaches below clamp profile bounds.");
if (front_wall_height > mount_flat_wall_height_nominal + 0.1)
    echo("WARNING: front wall extends below nominal flat-wall zone; relies on merge strip below flat section.");

if (holder_footprint_x > ender3_v3_bed_x || holder_footprint_y > ender3_v3_bed_y)
    echo("WARNING: holder-only footprint likely exceeds Ender 3 V3 bed (220x220 mm).");

// -------------------------------
// Helpers
// -------------------------------
function arc_angle_from_length(len, r) = (r > 0) ? (len / r) * 180 / PI : 0;
function arc_point(r, a_deg, cx) = [cx + r * cos(a_deg), r * sin(a_deg)];
function arc_points(r, a0_deg, a1_deg, n, cx) =
    [for (i = [0 : n]) arc_point(r, a0_deg + (a1_deg - a0_deg) * i / n, cx)];
function seg_count_for_span(a0_deg, a1_deg) = max(12, ceil(abs(a1_deg - a0_deg) / 3));

module annular_sector_span_2d(r_in, r_out, a0_deg, a1_deg, axis_r = shared_wall_radius) {
    if (r_out > r_in && abs(a1_deg - a0_deg) > 0.01) {
        cx = -axis_r;
        n = seg_count_for_span(a0_deg, a1_deg);

        polygon(points = concat(
            arc_points(r_out, a0_deg, a1_deg, n, cx),
            arc_points(r_in, a1_deg, a0_deg, n, cx)
        ));
    }
}

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
module interior_floor_blend_subtractor_linear() {
    blend_r = min(
        interior_corner_radius,
        (cavity_outer_radius - cavity_inner_radius) / 3,
        (back_wall_height - floor_thickness) / 3
    );
    trim_a = arc_angle_from_length(blend_r, cavity_ref_radius);

    if (
        blend_r > 0.2
        && cavity_outer_radius - blend_r > cavity_inner_radius + blend_r
        && (a_end - a_start) > (2 * trim_a + 0.5)
    ) {
        hull() {
            translate([0, 0, floor_thickness - join_eps])
                linear_extrude(height = join_eps)
                    annular_sector_span_2d(
                        cavity_inner_radius + blend_r,
                        cavity_outer_radius - blend_r,
                        a_start + trim_a,
                        a_end - trim_a
                    );

            translate([0, 0, floor_thickness + blend_r])
                linear_extrude(height = join_eps)
                    annular_sector_span_2d(cavity_inner_radius, cavity_outer_radius, a_start, a_end);
        }
    }
}

module holder_shell_extruded_linear() {
    difference() {
        linear_extrude(height = back_wall_height)
            annular_sector_span_2d(body_inner_radius, body_outer_radius, a_start, a_end);

        if (back_wall_height > floor_thickness) {
            open_a0 = a_start - end_wall_angle_thickness;
            open_a1 = a_end + end_wall_angle_thickness;

            translate([0, 0, floor_thickness])
                linear_extrude(height = back_wall_height - floor_thickness + join_eps)
                    annular_sector_span_2d(cavity_inner_radius, cavity_outer_radius, open_a0, open_a1);

            if (enable_interior_floor_blend)
                interior_floor_blend_subtractor_linear();
        }

        // Remove front/shared strip above fill-line rim to keep front wall lower.
        if (front_wall_height < back_wall_height) {
            translate([0, 0, front_wall_height])
                linear_extrude(height = back_wall_height - front_wall_height + join_eps)
                    annular_sector_span_2d(body_inner_radius, cavity_inner_radius, a_start, a_end);
        }
    }
}

module holder_side_walls_linear() {
    side_h = max(0, back_wall_height - floor_thickness + join_eps);
    wall_a = max(0.1, end_wall_angle_thickness);
    wall_join_a = arc_angle_from_length(0.2, centerline_radius);

    if (side_h > 0) {
        translate([0, 0, floor_thickness - join_eps])
            linear_extrude(height = side_h)
                annular_sector_span_2d(
                    body_inner_radius,
                    body_outer_radius,
                    a_start - wall_join_a,
                    min(a_end + wall_join_a, a_start + wall_a)
                );

        translate([0, 0, floor_thickness - join_eps])
            linear_extrude(height = side_h)
                annular_sector_span_2d(
                    body_inner_radius,
                    body_outer_radius,
                    max(a_start - wall_join_a, a_end - wall_a),
                    a_end + wall_join_a
                );
    }
}

module shared_wall_blend_linear() {
    if (enable_shared_wall_blend && shared_wall_blend_radius > 0) {
        blend_outer = min(cavity_outer_radius, cavity_inner_radius + shared_wall_blend_radius);
        blend_h = min(front_wall_height, floor_thickness + shared_wall_blend_radius);

        if (blend_outer > body_inner_radius && blend_h > 0) {
            linear_extrude(height = blend_h)
                annular_sector_span_2d(body_inner_radius, blend_outer, a_start, a_end);
        }
    }
}

module front_rim_round_cut_linear() {
    if (enable_front_rim_round && front_rim_round_radius > 0 && front_wall_height > floor_thickness) {
        fillet_r = front_rim_round_radius;
        fillet_center_r = max(0.1, cavity_inner_radius - fillet_r);

        translate([-shared_wall_radius, 0, front_wall_height - fillet_r])
            rotate([0, 0, a_start])
                rotate_extrude(angle = arc_angle_deg)
                    translate([fillet_center_r, 0])
                        circle(r = fillet_r, $fn = max(36, floor($fn / 2)));
    }
}

module end_mount_gusset_linear(side = -1) {
    if (enable_mount_gussets) {
        gusset_span = max(0.2, mount_gusset_span_deg);
        a0 = match_sweep_to_holder
            ? ((side < 0) ? (a_start + join_eps) : max(a_start, a_end - gusset_span))
            : ((side < 0) ? (a_start - gusset_span) : (a_end - join_eps));
        a1 = match_sweep_to_holder
            ? ((side < 0) ? min(a_end, a_start + gusset_span) : (a_end - join_eps))
            : ((side < 0) ? (a_start + join_eps) : (a_end + gusset_span));

        base_r0 = body_inner_radius;
        base_r1 = min(body_outer_radius, base_r0 + mount_gusset_base_depth);

        top_r0 = max(base_r0, body_outer_radius - mount_gusset_top_depth);
        top_r1 = body_outer_radius;

        top_z0 = max(floor_thickness, back_wall_height - mount_gusset_top_height);

        if (a1 > a0 && base_r1 > base_r0 + 0.1 && top_r1 > top_r0 + 0.1) {
            hull() {
                linear_extrude(height = mount_gusset_base_height)
                    annular_sector_span_2d(base_r0, base_r1, a0, a1);

                translate([0, 0, top_z0])
                    linear_extrude(height = mount_gusset_top_height)
                        annular_sector_span_2d(top_r0, top_r1, a0, a1);
            }
        }
    }
}

module holder_mount_gussets_linear() {
    end_mount_gusset_linear(-1);
    end_mount_gusset_linear(1);
}

module holder_linear() {
    difference() {
        union() {
            if (show_holder_shell) holder_shell_extruded_linear();
            if (show_holder_side_walls) holder_side_walls_linear();
            shared_wall_blend_linear();
            holder_mount_gussets_linear();
        }

        front_rim_round_cut_linear();
    }
}

module shared_wall_proxy_linear() {
    proxy_thickness = max(0.8, wall_thickness);
    proxy_h = min(back_wall_height, front_wall_height);

    if (proxy_h > 0) {
        linear_extrude(height = proxy_h)
            annular_sector_span_2d(max(0.1, body_inner_radius - proxy_thickness), body_inner_radius, a_start, a_end);
    }
}

module holder_local_placed() {
    // Back wall top sits at Z=0, basin drops downward by back_wall_height.
    translate([0, 0, -back_wall_height])
        holder_linear();
}

module holder_positioned() {
    attachment_frame(attach_angle_effective, shared_wall_radius, shared_wall_top_profile_y_sweep, 0)
        rotate([0, holder_tilt_deg, 0])
            holder_local_placed();
}

module holder_only_body() {
    rotate([0, holder_tilt_deg, 0])
        union() {
            holder_local_placed();
            if (holder_only_with_shared_wall_proxy)
                translate([0, 0, -back_wall_height])
                    shared_wall_proxy_linear();
        }
}

module holder_only_sample() {
    side_angle = (holder_only_side_print_edge == "end") ? a_end : a_start;
    sweep_match_deg = holder_only_side_print_match_sweep ? -side_angle : 0;

    if (holder_only_side_print) {
        rotate([holder_only_side_print_x_deg, 0, 0])
            rotate([0, 0, sweep_match_deg])
                holder_only_body();
    } else {
        holder_only_body();
    }
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
                    translate([shared_wall_attach_x, shared_wall_top_profile_y_2d])
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
