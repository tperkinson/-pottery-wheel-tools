# c_clamp_fit_coupon (v1)

## Purpose
- Fast-fit coupon for verifying C-clamp sweep vs. Brent splash pan radius.
- Uses only the canonical C-clamp profile (no pad, no attachments).
- Optional corner rounding removes the sharp outer back-right corner to reduce print time while keeping the top connected.

## Files
- `c_clamp_fit_coupon_v1.scad`
- `notes.md`

## Key Parameters
- `sweep_angle`: increase to test larger arc fit.
- `radius`: measured splash-pan radius.
- `radius_ref_mode`: `"hook_center"` or `"outer_edge"`.
- `round_outer_corner`: enable/disable corner rounding.
- `outer_corner_radius`: fillet radius at the outer corner.
- `shell_thickness`: hollow shell thickness (0 = solid).
- `back_wall_windows`: enable/disable back-wall windows.
- `window_depth`, `window_height`, `window_gap`, `window_count`: window sizing.
- `remove_back_wall`: remove the outer back wall for faster prints.
- `back_wall_cut_depth`, `back_wall_cut_top_margin`, `back_wall_cut_bottom_margin`: back-wall cut sizing.

## Fit/Test Log
- Date: 2026-02-05
- Printer/material:
- Layer/nozzle:
- Fit result:
- Next adjustment:

## Release Notes
- v1:
  - Initial clamp-only coupon with optional trim cut.
