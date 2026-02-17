# tool_shelf (v1)

## Purpose
- Curved radial shelf (annular sector) for holding tools/cleanup at the wheel.

## Files
- `tool_shelf_v1.scad`
- `notes.md`

## Geometry Proposal (Before Coding)
- Curved radial shelf (annular sector).
- Intended working area ~ 6" x 6" (152.4 mm x 152.4 mm).
- Taller lip on back and side edges; lower lip on the edge near me.
- Shelf placed at 8 o'clock with me at 6 o'clock (near-edge = my side).
- Add slight tilt for drainage toward the away-from-me edge.
- Smooth interior with large fillets, no trapped pockets.
- Use a printable gusset/brace; part will be printed on its side.

## Key Parameters
- `arc_length`
- `radial_width`
- `floor_thickness`
- `lip_thickness`
- `lip_height_near`, `lip_height_far`, `lip_height_sides`, `lip_height_side_end`
- `side_wall_thickness`, `side_wall_drop`
- `inner_overhang`, `corner_gap_size`, `lip_corner_radius`
- `clamp_cap_thickness`, `clamp_cap_width`
- `gusset_back_overhang`, `gusset_flare`, `gusset_top_flat`, `gusset_max_overhang_deg`
- `holder_tilt_deg`
- `holder_radial_location_on_pad`
- `gusset_thickness`, `gusset_height`, `gusset_width`
- `max_projection`

## Notes (v1)
- Geometry approach: annular-sector floor with plan-view fillets (`corner_radius`), lips on inner arc (far edge), outer arc (near edge), and both radial sides. Arc sweep is set by `arc_length` at the centerline radius; shelf is centered on the clamp sweep.
- Assumptions: near edge = outer arc (user side), far edge = inner arc (near C-clamp). `holder_radial_location_on_pad` is the inner-edge offset from the clamp wall. Floor top is aligned to clamp top (`max_profile_y = 0`).
- Drainage: small through-cut notch at the far (inner/clamp) edge plus `holder_tilt_deg` to drain toward the clamp side.
- Print alignment: all geometry is clipped to a shared annular-sector mask so every feature starts/stops at the same radial arc. `align_to_sweep_edges` keeps shelf sides aligned with clamp sweep ends for flat side printing.
- Reinforcement: single ramped gusset web (annular-sector hull) spans from clamp wall to shelf underside with overhang-limited slope for side printing (`gusset_max_overhang_deg`).
- Tuning order: 1) `holder_radial_location_on_pad` + `radial_width` (reach) 2) `arc_length` (sweep) 3) `holder_tilt_deg` (drain) 4) lip heights 5) floor/lip thickness 6) gusset dims 7) `corner_radius` / drain notch.
- V1 update: `inner_overhang` pushes the inner wall toward the clamp; `clamp_cap_*` thickens the clamp-side strip; `corner_gap_size` opens the inner-wall/side-wall corners; `lip_corner_radius` softens plan-view corners; `gusset_flare` reduces side-print overhang; optional `enable_clamp_channel` adds a shallow channel on the clamp-side strip.

## Fit/Test Log
- Date: 2026-02-05
- Printer/material:
- Layer/nozzle:
- Fit result:
- Next adjustment:

## Release Notes
- v1:
  - Initial scaffold from `templates/attachment_v1.scad`
