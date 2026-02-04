// YZ projection (side view)
projection(cut=false)
    rotate([0,90,0])
        import("SpongeHolder_export.stl");

color("red")
    union() {
        square([300, 0.5], center=true);
        square([0.5, 300], center=true);
    }
