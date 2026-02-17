# throwing_towel_holder (v1)

## Purpose
- Radial drape bar for a 16x30 hand towel (typically folded 16x15) with one-handed grab.

## Geometry Proposal (Pre-CAD)
- Radial bar axis points outward from wheel center (+X in local frame).
- Bar length capped to stay within 127 mm max projection from splash pan.
- 20 mm diameter bar with a small top retention lip and outer end stop.
- Shared C-cup wall: mount web overlaps the clamp flat wall instead of adding a redundant wall.
- Twin gusset plates and a wall web sized for wet towel load and tugging.
- Fully parameterized placement, retention, and strength controls.

## Files
- `throwing_towel_holder_v1.scad`
- `notes.md`

## Key Parameters
- `render_holder_only`
- `sweep_angle`, `radius`, `pad_length`, `pad_thickness`
- `holder_radial_location_on_pad`, `holder_tilt_deg`
- `bar_length`, `bar_diameter`, `bar_start_offset`, `bar_center_height`
- `retention_lip_height`, `retention_lip_width`
- `end_stop_diameter`, `end_stop_length`
- `gusset_thickness`, `gusset_height`, `gusset_width`
- `max_projection`

## Final Notes
- Geometry approach: linear radial bar + gusseted mount placed on swept clamp/pad; bar sits above pad plane with lip + end stop for towel retention.
- Shared-wall decision and details: mount web overlaps the C-cup flat wall by `shared_wall_overlap` to reuse the clamp wall as the inner mount face.
- Reinforcement choices: twin gusset plates plus a full-width wall web, sized for wet towel weight and tug loads in PETG/PLA.
- Defaults and assumptions: bar length 110 mm, diameter 20 mm, bar center 18 mm above pad; PETG/PLA; towel folded 16x15; max projection 127 mm.
- Parameter tuning order: fit/placement -> retention -> strength.

## Fit/Test Log
- Date: 2026-02-04
- Printer/material:
- Layer/nozzle:
- Fit result:
- Next adjustment:

## Release Notes
- v1:
  - Initial scaffold from `templates/attachment_v1.scad`
