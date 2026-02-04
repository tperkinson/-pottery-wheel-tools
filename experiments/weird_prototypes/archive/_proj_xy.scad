// XY projection (top view)
projection(cut=false)
    import("SpongeHolder_export.stl");

// axis crosshair
color("red")
    union() {
        square([300, 0.5], center=true);
        square([0.5, 300], center=true);
    }
