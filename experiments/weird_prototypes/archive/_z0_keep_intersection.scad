
// 2D intersection of Z=0 slice and keep box
intersection() {
    projection(cut=true)
        translate([0,0,-0.0])
            import("SpongeHolder_export.stl");
    translate([-2000.0, -2000.0])
        square([1969.0, 1987.0]);
}
