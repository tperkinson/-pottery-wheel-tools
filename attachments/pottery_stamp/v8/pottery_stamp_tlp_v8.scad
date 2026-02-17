
// TLP Pottery Stamp v8 (bigger base, SAME text size)
scale_factor = 0.6;   // 75% = 25% smaller
stamp_diameter = 38 * scale_factor;   // Increased base only
base_thickness = 6;
letter_height  = 2.8;
text_size      = 13* scale_factor;   // KEEP TEXT SAME SIZE

handle_base_d  = 14;//18;
handle_top_d   = 30;//30;
handle_height  = 22;
alignment_flat_depth = 2.0; // 0 disables the orientation flat
base_alignment_flat_depth = 1.4; // 0 disables base-pad orientation flat

module base_disk() {
    difference() {
        union() {
            cylinder(d=stamp_diameter, h=base_thickness-0.6, $fn=200);
            translate([0,0,base_thickness-0.6])
                cylinder(d1=stamp_diameter, d2=stamp_diameter-1.2, h=0.6, $fn=200);
        }
        if (base_alignment_flat_depth > 0)
            // Flat on the stamp pad perimeter to provide a second orientation cue.
            translate([0, -stamp_diameter/2 + base_alignment_flat_depth/2, base_thickness/2])
                cube([stamp_diameter * 1.2, base_alignment_flat_depth, base_thickness + 0.2], center=true);
    }
}

module stamp_text() {
    // Letters extrude DOWN so they contact clay first
    translate([0,0,0.15])
        mirror([0,1,0])
            mirror([1,0,0])
                translate([0,0,-letter_height])
                    linear_extrude(height=letter_height)
                        //text("T\u2665C",
                            text("TLP",
                             size=text_size,
                             halign="center",
                             valign="center",
                             font="DejaVu Sans:style=Bold",
                             spacing=1.0);
}

module mushroom_handle() {
    translate([0,0,base_thickness])
        difference() {
            cylinder(d1=handle_base_d, d2=handle_top_d, h=handle_height, $fn=140);
            if (alignment_flat_depth > 0)
                // Trim one side near the top so rotation is visible while stamping.
                translate([0, -handle_top_d/2 + alignment_flat_depth/2, handle_height/2])
                    cube([handle_top_d * 1.2, alignment_flat_depth, handle_height + 0.2], center=true);
        }
}

render(convexity=10)
rotate([180,0,0])
union() {
    base_disk();
    stamp_text();
    mushroom_handle();
}
