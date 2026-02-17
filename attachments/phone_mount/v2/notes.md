# Phone Mount Notes

## Files
- `phone_mount_v2.scad`: parametric phone holder on C-clamp platform.
- `phone_mount_v2.stl`: export target for this version.

## Current Design
- Clamp + pad are swept.
- Holder body is linear (not swept).
- Includes optional tilt brace for tilted holder support.
- Includes `render_holder_only` mode for fast fit-test prints.
- Sweep angle can be auto-derived from holder width to kiss the holder back corner.
- Holder geometry is clipped to the sweep side planes for clean printable side edges.

## Quick-Tune Inputs
- `holder_tilt_deg`
- `holder_rest_radial_offset`
- `holder_width`
- `holder_shelf_depth`
- `holder_stop_height`
- `auto_sweep_kiss_back_corner`
- `sweep_angle_manual`
- `sweep_angle_clearance`
