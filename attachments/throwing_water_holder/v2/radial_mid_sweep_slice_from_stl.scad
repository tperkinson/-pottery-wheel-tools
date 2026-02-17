// Mid-sweep radial section using prebuilt STLs (fast diagnostics).

$fn = 48;

slice_angle_deg = 12; // midpoint of 24 deg sweep

module assembly_from_stl() {
    import("../../../build/throwing_water_holder_v2_clamp_pad_only.stl");

    // Convert holder-only side-print orientation back into assembly orientation.
    rotate([90, 0, 0])
        translate([234.891978, 0, 16])
            rotate([0, -90, 0])
                import("../../../build/throwing_water_holder_v2.stl");
}

projection(cut = true)
    rotate([0, slice_angle_deg, 0])
        assembly_from_stl();
