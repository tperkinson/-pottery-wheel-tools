
// TLP Pottery Stamp v8 (bigger base, SAME text size)
scale_factor = 0.6;   // 75% = 25% smaller
stamp_diameter = 38 * scale_factor;   // Increased base only
base_thickness = 6;
letter_height  = 2.8;
text_size      = 13* scale_factor;   // KEEP TEXT SAME SIZE

handle_base_d  = 18;
handle_top_d   = 30;
handle_height  = 22;

module base_disk() {
    union() {
        cylinder(d=stamp_diameter, h=base_thickness-0.6, $fn=200);
        translate([0,0,base_thickness-0.6])
            cylinder(d1=stamp_diameter, d2=stamp_diameter-1.2, h=0.6, $fn=200);
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
        cylinder(d1=handle_base_d, d2=handle_top_d, h=handle_height, $fn=140);
}

render(convexity=10)
rotate([180,0,0])
union() {
    base_disk();
    stamp_text();
    mushroom_handle();
}
