# AGENTS.md

Project guidance for coding/design assistants working in `pottery-wheel-tools`.

## Scope
- Treat `pottery-wheel-tools/` as the project root.
- Keep `core_mount_system/` stable; new designs should usually go under `attachments/`.

## Canonical Mount References
- Canonical clamp profile: `core_mount_system/c_clamp/v1/c_clamp_profile_topref_v1.scad`
- Canonical sweep reference: `core_mount_system/c_clamp/v1/c_clamp_sweep_reference_v1.scad`
- Do **not** re-derive clamp geometry from STL when profile points already exist.

## Coordinate / Geometry Rules
- Clamp profile is top-referenced: `max_profile_y = 0`.
- "Top" means near `Y = 0` in profile space.
- Preserve top anchor unless explicitly asked to change core geometry.
- For linear (non-swept) attachments, use local frame:
  - `+X`: radial outward
  - `+Y`: tangent direction
  - `+Z`: profile-up
- Keep swept parts (clamp/pad) and linear attachment bodies separated structurally in code.

## Attachment Conventions
- Path convention: `attachments/<attachment_name>/vN/`
- File convention:
  - SCAD: `<attachment_name>_vN.scad`
  - STL: `<attachment_name>_vN.stl`
  - Notes: `notes.md`
- Prefer parameter sections:
  - Quick Tuning (common)
  - Strength / Printability (common)
  - Advanced Controls
  - Derived values
- Include `render_holder_only` (or equivalent) for fast test prints whenever practical.

## Build / Validation
- Use `make check` for quick compile/export checks.
- Use `make all` for primary STL exports.
- Keep generated files under `build/`.

## Experiments
- Place unfinished work in `experiments/`.
- Promote only validated designs into versioned `attachments/` folders.
