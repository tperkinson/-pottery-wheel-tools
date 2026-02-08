# throwing_water_holder (v1)

## Geometry approach used
- Native annular-sector basin (designed radial, not clipped from a box).
- Two radial side walls define the span, with side 1 starting at `0 deg` when `match_side_walls_to_sweep=true`.
- Front/close wall and back wall are both radial arcs.
- Front-to-back top height transitions by a smooth radial profile (`smoothstep`) so there is no stepped front-side notch.
- Large rounding is applied to:
  - plan seams (`plan_corner_round_radius`)
  - front rim (`front_rim_round_radius`)
  - back rim (`back_rim_round_radius`)
  - side top seams (`side_top_round_radius`)
  - front-side top corners (`front_side_corner_round_radius`)
  - interior floor blend (`interior_floor_blend_radius`)

## Shared-wall implementation details
- Mounting uses canonical clamp profile:
  - `core_mount_system/c_clamp/v1/c_clamp_profile_topref_v1.scad`
- Top reference behavior is preserved (`max_profile_y = 0` from canonical profile).
- Basin front wall is merged into the C-cup wall via `shared_wall_overlap`; no redundant parallel front wall is added.
- Clamp/pad sweep geometry remains separate from holder geometry.

## Stability / reinforcement choices
- PETG-oriented minimum structure defaults:
  - `wall_thickness = 3.6`
  - `floor_thickness = 4.5`
- Side/top/front corner rounds were increased to remove sharp stress risers.
- Smooth interior blend avoids debris traps and supports easier cleaning.

## Final assumptions/defaults
- `target_volume_ml = 946`
- `volume_headroom_ml = 120`
- `sweep_angle = 24`
- `match_side_walls_to_sweep = true`
- `arc_length = 102` (used for non-sweep mode and consistency checks)
- `radial_width = 135`
- `depth = 72`
- `back_wall_height = 72`
- `front_wall_height = 64`
- `holder_top_offset = 16`
- `holder_radial_location_on_pad = 0`
- `holder_tilt_deg = 2`
- Derived default estimate:
  - fill-line volume: `~958 ml`
  - max volume: `~1087 ml`

## Parameter tuning order
1. Fit first: `holder_top_offset`, `holder_radial_location_on_pad`, `holder_tilt_deg`
2. Capacity second: `radial_width`, `depth` / `back_wall_height`, `front_wall_height`
3. Splash behavior third: `front_wall_height`, `back_wall_height`, `side_wall_sweep_margin_deg`
4. Organic smoothing last: `plan_corner_round_radius`, `side_top_round_radius`, `front_side_corner_round_radius`, `front_rim_round_radius`, `back_rim_round_radius`
