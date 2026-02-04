// Y-axis sweep using direct STL slice at Z=0 (authoritative)
// Monolithic, trimmed to keep box

$fn = 200;

slice_z = 0.0;
show_profile = true;          // true: render 2D profile, false: 3D swept clamp
show_axis = true;             // show axis marker in 2D profile view
axis_marker_r = 2;

// Keep box used during bake (in axis space)
keep_x = -2000.0;
keep_y = -2000.0;
keep_w = 1969.0;
keep_h = 1987.0;

// Sweep parameters (Y-axis sweep)
sweep_angle = 120.0;
axis_x = 0.0;
axis_z = 0.0;
axis_shift_x = 53.177251;

profile_points = [
    [-52.070450, -66.944245],
    [-52.287491, -67.146744],
    [-52.482041, -67.370941],
    [-52.651924, -67.614350],
    [-52.795250, -67.874291],
    [-52.910454, -68.147858],
    [-52.996231, -68.432022],
    [-53.051663, -68.723633],
    [-53.076092, -69.019455],
    [-53.077251, -69.080277],
    [-53.076714, -69.162904],
    [-53.054043, -69.464883],
    [-52.999100, -69.762681],
    [-52.912529, -70.052872],
    [-52.795318, -70.332093],
    [-52.648819, -70.597123],
    [-52.474731, -70.844910],
    [-52.275070, -71.072579],
    [-52.052123, -71.277512],
    [-51.808471, -71.457337],
    [-51.546932, -71.609986],
    [-51.270530, -71.733689],
    [-50.982444, -71.827019],
    [-50.686012, -71.888901],
    [-50.384643, -71.918617],
    [-50.302052, -71.921082],
    [-50.302048, -71.921081],
    [-48.769562, -71.885910],
    [-46.907101, -71.684464],
    [-45.071487, -71.310425],
    [-43.600781, -70.878258],
    [-41.808557, -70.291007],
    [-40.087681, -69.519348],
    [-38.457050, -68.571732]
];

module raw_profile() {
    polygon(points=profile_points);
}

module clamp_profile() {
    translate([axis_shift_x, 0])
        translate([-axis_x, -axis_z])
            raw_profile();
}

if (show_profile) {
    clamp_profile();
    if (show_axis) {
        color("red")
            translate([axis_shift_x, 0])
                circle(r=axis_marker_r, $fn=48);
    }
} else {
    rotate([90,0,0])
        rotate_extrude(angle=sweep_angle)
            clamp_profile();
}
