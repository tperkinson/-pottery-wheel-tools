# throwing_water_holder (v1)

## Purpose
- Open throwing-water basin using the canonical C-clamp/C-cup mount.
- Working fill target: `32 oz` / `946 ml` at fill line (not a cup holder).

## Files
- `throwing_water_holder_v1.scad`
- `notes.md`

## Geometry Proposal (Before Implementation)
- Use canonical swept mount geometry from `core_mount_system/c_clamp/v1/c_clamp_profile_topref_v1.scad` and keep top-reference behavior (`max_profile_y = 0`).
- Build basin as a single annular-sector shell in holder space (non-swept holder geometry), then place it onto the sweep frame.
- Reuse the mount flat C-cup wall as the basin front/shared wall:
  - no separate redundant front wall
  - only a controlled merge strip for structural continuity
- Keep basin low-profile (`depth` target band ~`50-65 mm`) and get capacity from footprint first (`arc_length` + `radial_width`).
- Open top, no drain holes.
- Back wall taller than front wall for slosh control at throwing speeds.
- Add heavy-load reinforcement:
  - shared-wall blend thickening
  - end gusset/brace ribs at mount interface zones
- Keep interior cleanable:
  - smooth shell via continuous boolean solids
  - floor/wall blend radius features
  - no trapped internal cavities

## Final Geometry Approach (Implemented)
- Mount geometry is kept as canonical swept profile + optional pad; holder geometry is separate linear modules and then positioned in sweep frame.
- Basin shell is an annular-sector body with:
  - open top
  - no drain holes
  - interior cavity subtraction with floor blend helper for smoother clean-out transitions
- Back wall is intentionally taller than front wall:
  - front wall = fill-line side
  - back wall = slosh-control side for wheel motion
- `render_holder_only` mode is implemented for quick fit/volume iteration.

## Shared-Wall Implementation Details
- Shared wall reference is the canonical mount wall at `max_profile_x`.
- Basin front uses a merge strip (`shared_wall_overlap`) where holder and mount intersect into one continuous load path.
- No extra parallel full-height basin front wall is added apart from that merge strip.
- Holder-only mode can show a shared-wall proxy for visual fit checks.

## Stability / Reinforcement Choices
- PETG-robust wall/floor defaults (`wall_thickness = 3.6`, `floor_thickness = 4.5`).
- Front shared-wall blend thickening (`shared_wall_blend_radius`) to reduce stress concentration at the mount junction.
- Dual end gusset braces (`enable_mount_gussets = true`) sized for wet-load handling shocks.
- Side walls and floor remain continuous solids (no trapped reinforcement cavities).

## Final Assumptions And Defaults
- Canonical mount profile: `core_mount_system/c_clamp/v1/c_clamp_profile_topref_v1.scad`
- Top-reference behavior preserved (`max_profile_y = 0`), with holder back rim offset via `holder_top_offset = 6.5`.
- Repo splash-pan defaults used (`radius = 222.25`, `radius_ref_mode = "hook_center"`).
- Capacity defaults:
  - `target_volume_ml = 946`
  - `volume_headroom_ml = 105`
- Basin defaults:
  - `arc_length = 172.3`
  - `radial_width = 110`
  - `depth = 58`
  - `holder_radial_location_on_pad = radial_width / 2`
  - `front_wall_height = depth + floor_thickness - 6`
  - `back_wall_height = depth + floor_thickness`
  - `match_sweep_to_holder = true` (`sweep_side_margin_deg` ignored when true)
  - `front_rim_round_radius = 3.0` (rounds the top inner edge of the front/shared wall on the basin side)
  - Optional toggles: `enable_shared_wall_blend = true`, `enable_interior_floor_blend = true`, `enable_front_rim_round = true`
- Derived estimate at defaults:
  - fill-line volume ≈ `947 ml`
  - headroom ≈ `109 ml`

## Required Parameter Set (Implemented)
- `target_volume_ml`
- `volume_headroom_ml`
- `arc_length`
- `radial_width`
- `depth`
- `wall_thickness`
- `floor_thickness`
- `holder_tilt_deg`
- `holder_radial_location_on_pad`
- `back_wall_height`
- `front_wall_height`

## Planned Checks/Warnings
- Echo estimated fill-line basin volume (`ml`) and headroom estimate.
- Warn if fill-line estimate < `target_volume_ml`.
- PETG thinness warnings for walls/floor/shared overlap/gusset dimensions.
- Clamp/pad/sweep interference warnings.
- Warn if holder-only footprint likely exceeds `220 x 220` mm bed.

## Mount Position Intent
- Geometry defaults target use around wheel `10 o'clock` by keeping the basin centered within the sweep and tuned for outward footprint.
- Use repo default splash-pan geometry values unless user fit data proves otherwise.

## Validation/Warn Logic Implemented
- Echoes estimated fill-line volume and headroom in `ml`.
- Warns when fill-line volume is below `target_volume_ml`.
- Warns on PETG-thin settings (wall/floor/overlap/gusset dimensions).
- Warns for sweep/pad/interference-risk envelope violations.
- Warns if holder-only footprint likely exceeds Ender 3 V3 (`220x220`).
- Warns if sweep/holder alignment is requested but `holder_angle_offset` is nonzero.
- Warns on overly small/large `front_rim_round_radius`.

## Holder-Only Side-Print Option
- `holder_only_side_print = true` rotates the holder-only sample onto its side.
- `holder_only_side_print_match_sweep = true` aligns the sweep edge flat to the bed before side-rotation.
- `holder_only_side_print_edge` selects `"start"` or `"end"` sweep edge to lay down.
- `holder_only_side_print_x_deg` controls the side rotation (use `-90` for opposite).

## Sweep Alignment Option
- `match_sweep_to_holder = true` forces sweep angle to match the holder arc (edges align).
- When `match_sweep_to_holder = false`, `sweep_side_margin_deg` adds clearance beyond the holder arc.
- When `match_sweep_to_holder = true`, end gussets are clamped inside the holder arc so they do not exceed the sweep edges.

## Parameter Tuning Order
1. Fit to mount and placement: `holder_top_offset`, `holder_radial_location_on_pad`, then `holder_tilt_deg`.
2. Capacity target: `arc_length` first, then `radial_width`, then `depth`.
3. Fill-line and splash behavior: `front_wall_height` (fill line) then `back_wall_height` (slosh margin/headroom).
4. Structural margin: `wall_thickness`, `floor_thickness`, `shared_wall_overlap`, gusset parameters.
5. Cleanability finish: `interior_corner_radius` and `shared_wall_blend_radius`.

## Fit/Test Log
- Date: 2026-02-04
- Printer/material:
- Layer/nozzle:
- Fit result:
- Next adjustment:

## Release Notes
- v1:
  - Implemented open annular-sector throwing-water basin with shared mount wall.
  - Added fill-line volume/headroom estimation + warning checks.
  - Added PETG thickness and interference/bed-envelope warnings.
  - Added heavy-load shared-wall blend and dual end gusset reinforcement.
  - Added `render_holder_only` mode and Makefile export/check integration.
