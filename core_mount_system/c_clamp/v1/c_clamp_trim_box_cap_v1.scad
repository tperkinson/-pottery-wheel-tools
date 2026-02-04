// Trim the bottom of the C-clamp by a box and re-cap with a semicircle
// Parameters are easy to tweak for 4.0/4.5/5.0 mm, etc.

include <c_clamp_profile_z0_keep_v1.scad>;

// The profile points in c_clamp_profile_z0_keep_v1.scad were shifted
// so min X/Y = 0. These offsets put them back in the original SVG coordinate space.
// If your SVG changes, adjust these two numbers.
offset_x = -58.077; // original min X
offset_y = 13.0;    // original min Y

// User-facing parameters (SVG Y increases downward)
cut_depth = 4.5;       // mm to remove in X (net), tweak to 4.0 or 5.0 if needed
band_y_top_svg = 58.0; // top of trim band in SVG coords (make larger if needed)
band_y_bottom_svg = 74.0; // bottom of trim band in SVG coords
cap_radius = 2.9;      // mm; rounded endcap radius
// Cut box extends further right so the cap can be added back cleanly.
// Set this to cap_radius to avoid a flat end at x_target.
cut_box_extra_x = cap_radius;
show_guides = true;
$fn = 96;

// Helper: unshift profile points back to SVG coords
profile_points_unshifted = [
    for (p = profile_points) [p[0] + offset_x, p[1] + offset_y]
];

function min_in_band(points, y0, y1) =
    min([for (p = points) if (p[1] >= y0 && p[1] <= y1) p[0]]);

// Intersections of the profile with a vertical line x_line, within a Y band.
function intersect_ys(points, x_line, y0, y1) = [
    for (i = [0 : len(points) - 1])
        let(p1 = points[i], p2 = points[(i + 1) % len(points)])
        let(x1 = p1[0], y1p = p1[1], x2 = p2[0], y2p = p2[1])
        let(crosses = (x1 - x_line) * (x2 - x_line) <= 0 && x1 != x2)
        if (crosses)
            let(t = (x_line - x1) / (x2 - x1))
            let(y = y1p + t * (y2p - y1p))
            if (t >= 0 && t <= 1 && y >= y0 && y <= y1) y
];

// SVG Y increases downward, but OpenSCAD Y increases upward.
// Convert SVG band to OpenSCAD Y by flipping around the min/max of the profile.
min_y = min_profile_y + offset_y;
max_y = max_profile_y + offset_y;
function svg_to_scad_y(y_svg) = (min_y + max_y) - y_svg;

band_y_top = svg_to_scad_y(band_y_top_svg);
band_y_bottom = svg_to_scad_y(band_y_bottom_svg);

// Ensure top/bottom ordering in OpenSCAD space
band_y_min = min(band_y_top, band_y_bottom);
band_y_max = max(band_y_top, band_y_bottom);

// x_target is the net removal plane (cut_depth from the original leftmost).
// x_box is the actual cut plane; the cap will extend back to x_target.
x_left = min_in_band(profile_points_unshifted, band_y_min, band_y_max);
x_target = x_left + cut_depth;
x_box = x_target + cut_box_extra_x;

cap_r = min(cap_radius, (band_y_max - band_y_min) / 2);
// Center the cap on the remaining geometry at the actual cut plane (x_box)
cap_ys = intersect_ys(profile_points_unshifted, x_box, band_y_min, band_y_max);
cap_center_y = (len(cap_ys) >= 2) ? (min(cap_ys) + max(cap_ys)) / 2 : (band_y_min + band_y_max) / 2;
cap_center = [x_target + cap_r, cap_center_y];

module base_profile() {
    polygon(points = profile_points_unshifted);
}

module cut_box() {
    // Big box to remove everything left of x_cut within the band
    translate([x_left - 200, band_y_min])
        square([x_box - x_left + 200, band_y_max - band_y_min]);
}

module cap() {
    // Semicircle that starts at x_cut and stays to the right of it
    intersection() {
        translate(cap_center) circle(r = cap_r);
        translate([x_target, band_y_min])
            square([2 * cap_r, band_y_max - band_y_min]);
    }
}

module trimmed_profile() {
    union() {
        difference() {
            base_profile();
            cut_box();
        }
        cap();
    }
}

module guides() {
    color([1, 0, 0, 0.15])
        translate([x_left, band_y_min])
            square([x_box - x_left, band_y_max - band_y_min]);
    color([1, 0, 0, 1])
        translate([x_target, band_y_min])
            square([0.25, band_y_max - band_y_min]);
    color([1, 0, 0, 0.7])
        translate([x_box, band_y_min])
            square([0.25, band_y_max - band_y_min]);
    // mark cap center
    color([0, 0.6, 0, 0.7])
        translate(cap_center) circle(r = 0.4, $fn = 24);
}

// Use background (%) so guides never affect the actual geometry
if (show_guides) %guides();

trimmed_profile();
