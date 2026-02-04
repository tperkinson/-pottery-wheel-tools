// XZ projection (front view)
projection(cut=false)
    rotate([90,0,0])
        import("SpongeHolder_export.stl");

color("red")
    union() {
        square([300, 0.5], center=true);
        square([0.5, 300], center=true);
    }
