# throwing_water_holder (v3 build123d migration)

## Purpose
- build123d port of `v2c` with the same mount reference frame and the same default tuning values.
- Keep clamp/pad sweep geometry separate from holder-body geometry so fit fixes and basin fixes can be iterated independently.

## What was migrated from v2c
- Parameter defaults copied from `attachments/throwing_water_holder/v2/throwing_water_holder_v2c.scad`.
- Same derived frame math for:
  - sweep radius anchoring (`radius_ref_mode`, `radius`, `axis_z`)
  - holder placement (`holder_top_offset`, `holder_radial_location_on_pad`, `holder_tilt_deg`)
  - side-wall span and inner angular wall-thickness offset
  - volume checks (`fill-line` and `max` estimates)
- Holder body remains an annular-sector shell with front/back radial walls and side walls aligned to sweep ends when `match_side_walls_to_sweep=true`.

## Workflow (fast iteration)
- Preview (default when no args):
  - `python cad/build123d/attachments/throwing_water_holder/v3/throwing_water_holder_v3.py`
- Preview + export:
  - `python cad/build123d/attachments/throwing_water_holder/v3/throwing_water_holder_v3.py --preview --export`
- Export only:
  - `python cad/build123d/attachments/throwing_water_holder/v3/throwing_water_holder_v3.py --export`
- Holder-only sample export:
  - `python cad/build123d/attachments/throwing_water_holder/v3/throwing_water_holder_v3.py --holder-only --export`
- Make targets:
  - `make PYTHON_B123D=.venv-b123d/bin/python throwing_water_holder_b123d`
  - `make PYTHON_B123D=.venv-b123d/bin/python throwing_water_holder_b123d_holder_only`

## Tuning checklist (recommended order)
1. Fit to wheel/mount:
   - `holder_top_offset`
   - `holder_radial_location_on_pad`
   - `holder_tilt_deg`
2. Capacity / reach:
   - `radial_width`
   - `depth`, `front_wall_height`, `back_wall_height`
3. Splash behavior:
   - `sweep_angle`
   - front/back wall height relationship
4. Printability and feel:
   - `wall_thickness`
   - `floor_thickness`
   - `plan_corner_round_radius`
   - `interior_floor_blend_radius`
   - `top_edge_round_radius`

## Known migration deltas vs v2c
- `v3` keeps all v2c rounding controls but applies them with a simpler OCC fillet strategy.
- Corner/rim smoothing is very close for default values, but not bit-for-bit equivalent to v2c's full cutter stack.
- Clamp/pad reference geometry still comes from the canonical `core_mount_system` profile source.
