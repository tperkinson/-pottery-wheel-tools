// Parametric rebuild of SpongeHolder clamp (arc/line fit)
// Monolithic version (no STL import)
// Fit tolerance: 0.2mm

// Parametric rebuild of SpongeHolder clamp from STL slice
// Monolithic version (no STL import)
// Uses Z-slice profile, swept around Y axis
$fn = 200;  // increase sweep smoothness
// Parametric rebuild of SpongeHolder clamp from STL slice
// Step 1: Extract 2D profile (Z-slice) and trim tray
slice_z = 93.340206;          // Z slice height (from STL mid-plane)
show_profile = false;          // true: render 2D profile, false: 3D swept clamp
show_axis = true;             // show axis marker in 2D profile view
axis_marker_r = 2;
// Tray removal (adjust to trim the flat tray) - coordinates are in AXIS space
tray_cut_x = 228.277581;             // everything to the right of this gets removed
tray_cut_y = -196.481317;
tray_cut_w = 2000;
tray_cut_h = 2000;
// Top removal (adjust to trim any remaining tray at the top of the C-cup) - AXIS space
enable_top_cut = true;
top_cut_y = -11.781317;          // everything above this gets removed
top_cut_x = -1722.022419;
top_cut_w = 4000;
top_cut_h = 2000;
// Sweep parameters
sweep_angle = 42;            // degrees
axis_x = -277.977581;             // estimated axis center X (auto)
axis_y = -3.518683;             // estimated axis center Y (auto)
axis_shift_x = 0.000000;        // shift profile so all X >= 0 for rotate_extrude

// Arc/line segments (in axis space)
segments = [
    ["line", 214.435834, -67.359575, 216.946507, -66.456317],
    ["arc", 210.585963, -49.185557, 18.463031, -1.217927, -0.296605],
    ["line", 228.234247, -54.579225, 228.264910, -24.387933],
    ["line", 228.264910, -24.387933, 200.391089, -29.483434],
    ["line", 200.391089, -29.483434, 205.945532, -18.947513],
    ["arc", 214.402973, -25.995621, 11.044487, 0.818411, 2.446838],
    ["line", 221.950866, -17.932172, 224.801560, -24.482503],
    ["line", 224.801560, -24.482503, 205.945517, -62.983168],
    ["line", 205.945517, -62.983168, 213.026280, -67.734440],
    ["line", 213.026280, -67.734440, 214.435834, -67.359575]
];

function arc_points(cx, cy, r, a0, a1, n) =
    [for (i=[0:n]) [cx + r*cos(a0 + (a1-a0)*i/n), cy + r*sin(a0 + (a1-a0)*i/n)]];

function line_points(x0, y0, x1, y1, n) =
    [for (i=[0:n]) [x0 + (x1-x0)*i/n, y0 + (y1-y0)*i/n]];

function drop_first(arr) =
    [for (i=[1:len(arr)-1]) arr[i]];

function seg_points(seg, is_first) =
    seg[0] == "arc"
        ? (let(n = max(4, ceil(abs(seg[5]-seg[4]) / (5*PI/180))))
           (is_first ? arc_points(seg[1],seg[2],seg[3],seg[4],seg[5],n)
                    : drop_first(arc_points(seg[1],seg[2],seg[3],seg[4],seg[5],n))))
        : (let(n = 1)
           (is_first ? line_points(seg[1],seg[2],seg[3],seg[4],n)
                    : drop_first(line_points(seg[1],seg[2],seg[3],seg[4],n))));

function path_points(segs, i=0) =
    i >= len(segs) ? [] :
        concat(seg_points(segs[i], i==0), path_points(segs, i+1));

module raw_profile() {
    polygon(points=path_points(segments));
}

module clamp_profile() {
    // Profile already in axis space (with shift and cuts baked into segments)
    raw_profile();
}

if (show_profile) {
    clamp_profile();
    if (show_axis) {
        color("red")
            translate([0,0])
                circle(r=axis_marker_r, $fn=48);
    }
} else {
    rotate([90,0,0])
        rotate_extrude(angle=sweep_angle)
            clamp_profile();
}
