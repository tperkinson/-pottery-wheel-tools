# throwing_water_holder (v2)

## Purpose
- Open-top throwing water holder for the C-clamp mount with no sharp seams inside or outside.
- Same overall capacity target as v1, but with rounded seams enabled by default.

## Geometry approach used
- Native annular-sector basin (radial geometry, not a clipped rectangular block).
- Side walls align with sweep endpoints (`a_start = 0 deg`, `a_end = sweep span`).
- Mount wall and opposite wall are radial arcs.
- Constant wall/floor thickness is preserved through radial + angular offset math.
- Clamp/pad sweep geometry remains separate from holder body geometry.

## Smoothing strategy
- Plan corner rounding (`plan_corner_round_radius`) creates rounded vertical wall intersections.
  - Outer and inner corner rounds are applied separately to better preserve wall thickness at wall-wall seams.
- Interior floor blend (`interior_floor_blend_radius`) rounds all inner floor-to-wall seams.
- Exterior floor blend mirrors the same radius so inside/outside floor feel consistent.
- Top-edge rounding defaults on:
  - `front_rim_round_radius`
  - `back_rim_round_radius`
  - `side_top_round_radius`
  - `front_side_corner_round_radius`
  - `back_side_corner_round_radius` (new in v2)

## Defaults in v2
- `target_volume_ml = 946`
- `volume_headroom_ml = 120`
- `sweep_angle = 24`
- `radial_width = 135`
- `depth = 72`
- `wall_thickness = 4.8`
- `floor_thickness = 4.5`
- `plan_corner_round_radius = 8`
- `interior_floor_blend_radius = 4.0`
- `top_edge_round_radius = 2.2` (drives all top rim/corner rounds)
- `holder_top_offset = 16`
- `holder_radial_location_on_pad = 0`
- `holder_tilt_deg = 0`

## Parameter tuning order
1. Fit: `holder_top_offset`, `holder_radial_location_on_pad`, `holder_tilt_deg`
2. Capacity: `radial_width`, `depth`, `front_wall_height`, `back_wall_height`
3. Splash behavior: `sweep_angle`, wall heights
4. Feel/cleanability: `plan_corner_round_radius`, `interior_floor_blend_radius`, `top_edge_round_radius`

## Release notes
- v2:
  - Starts from v1 radial basin approach.
  - Enables top seam rounding by default.
  - Adds explicit back top-corner rounding to remove remaining sharp points.
