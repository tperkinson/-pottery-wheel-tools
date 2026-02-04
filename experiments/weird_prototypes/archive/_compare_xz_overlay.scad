// Overlay XZ projections: original STL (black) vs current model (red)

// Original
color("black")
projection(cut=false)
    rotate([90,0,0])
        import("SpongeHolder_export.stl");

// Current
color("red")
projection(cut=false)
    rotate([90,0,0])
        import("_clamp_current.stl");
