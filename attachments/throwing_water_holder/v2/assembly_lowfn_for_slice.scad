// Low-detail assembly export used only for fast section diagnostics.

$fn = 40;

use <throwing_water_holder_v2.scad>;

union() {
    clamp_pad_sweep();
    holder_positioned();
}
