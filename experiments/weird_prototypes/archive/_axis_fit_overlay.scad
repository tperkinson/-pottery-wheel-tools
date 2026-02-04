// Overlay STL slice with fitted circle center/radius
slice_z = 93.340206;
fit_cx = -74.9135;
fit_cy = 188.5724;
fit_r  = 222.25;

// STL slice
color("black")
projection(cut=true)
    translate([0,0,-slice_z])
        import("SpongeHolder_export.stl");

// Fitted circle (axis)
color("red")
translate([fit_cx, fit_cy])
    circle(r=fit_r, $fn=360);

// Axis center mark
color("red")
translate([fit_cx, fit_cy])
    circle(r=3, $fn=36);
