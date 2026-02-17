# throwing_towel_holder (v2)

## Purpose
- Radial drape bar for a 16x30 hand towel (typically folded 16x15) with one-handed grab.

## Geometry Proposal (Pre-CAD)
- Keep radial bar + retention lip + end stop from v1.
- Reduce shared-wall web above clamp top; embed the web below the top for true load sharing.
- Add clamp-side gussets (back side of the web) to stiffen the connector in bending.
- Add holder-only print orientations to simplify test prints.

## Files
- `throwing_towel_holder_v2.scad`
- `notes.md`

## Key Parameters
- `render_holder_only`, `holder_only_print_mode`
- `sweep_angle`, `radius`, `pad_length`, `pad_thickness`
- `holder_radial_location_on_pad`, `holder_tilt_deg`
- `bar_length`, `bar_diameter`, `bar_start_offset`, `bar_center_height`
- `retention_lip_height`, `retention_lip_width`
- `end_stop_diameter`, `end_stop_length`
- `gusset_thickness`, `gusset_height`, `gusset_width`
- `web_embed_depth`, `web_height_above_top`
- `back_gusset_enable`, `back_gusset_depth`, `back_gusset_height`
- `max_projection`

## Final Notes
- Geometry approach: linear radial bar + gusseted mount placed on swept clamp/pad. Web is shorter above the clamp and embedded below the top for actual load sharing.
- Shared-wall decision and details: web overlaps the C-cup flat wall by `shared_wall_overlap`, with `web_embed_depth` set to push into the clamp wall.
- Reinforcement choices: dual-sided gusset plates (front + back) plus a bar mount block to spread load into the bar.
- Defaults and assumptions: bar length 110 mm, diameter 20 mm, bar center 18 mm above pad; PETG/PLA; towel folded 16x15; max projection 127 mm.
- Parameter tuning order: fit/placement -> retention -> strength.

## Fit/Test Log
- Date: 2026-02-05
- Printer/material:
- Layer/nozzle:
- Fit result:
- Next adjustment:

## Release Notes
- v2:
  - Shorter shared-wall web above top + embedded web below top.
  - Added clamp-side gussets for connector stiffness.
  - Added holder-only print orientation controls.
