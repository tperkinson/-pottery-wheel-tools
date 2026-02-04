// Overlay XZ projections: original STL (black) vs current model (red, shifted)

// Original
color("black")
projection(cut=false)
    rotate([90,0,0])
        import("SpongeHolder_export.stl");

// Current (shifted +15 in X to reveal)
color("red")
projection(cut=false)
    translate([15,0,0])
        rotate([90,0,0])
            import("_clamp_current.stl");
