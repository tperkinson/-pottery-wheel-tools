# Dimensions and Tolerances

## Core Profile Extents (from `../c_clamp/v1/c_clamp_profile_topref_v1.scad`)
- `min_profile_x = -14.0407 mm`
- `max_profile_x = 13.0363 mm`
- `min_profile_y = -58.4338 mm`
- `max_profile_y = 0.0000 mm`
- `hook_center_x = 0.394322 mm`
- `hook_center_r = 9.774756 mm`

## Sweep Baseline
- Typical radius: `222.25 mm`
- Typical sweep angle range used in this project: `20°` to `45°`
- Radius reference default: `hook_center`

## Suggested Print Fit Defaults
- General FDM assembly clearance target: `0.25` to `0.35 mm`
- Thin structural wall minimum for load-bearing: `>= 3.0 mm`
- Joint/brace contact overlap target: `>= 1.0 mm`

## Notes
- Keep the top anchor (`max Y = 0`) fixed when creating derivatives.
- If attachment tilt is introduced, reinforce the base with a brace/gusset.
