
difference() {
    projection(cut=true)
        translate([0,0,0])
            import("SpongeHolder_export.stl");
    translate([-2000, -2000])
        square([1969, 1987]);
}
