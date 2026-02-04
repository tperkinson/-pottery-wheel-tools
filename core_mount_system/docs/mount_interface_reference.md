# Mount Interface Reference

## Canonical Clamp Profile
- Source file: `../c_clamp/v1/c_clamp_profile_topref_v1.scad`
- Use as canonical geometry: do not re-derive from STL.
- Profile anchor is top-referenced: `max Y = 0`.
- "Top" means near `Y = 0` in profile space.

## Clamp Construction
- 2D profile:
  - `polygon(points = profile_points);`
- Sweep reference:
  - `../c_clamp/v1/c_clamp_sweep_reference_v1.scad`
  - Default radius reference mode: `hook_center`
  - Tunable: `sweep_angle`, `radius`, `axis_z`

## Attachment Integration Rules
- Build attachment intent in the same profile coordinate space.
- Keep swept clamp/pad geometry separate from non-swept attachment bodies.
- For linear attachments, use a clear local frame:
  - `+X`: radial outward
  - `+Y`: tangent direction
  - `+Z`: profile-up
