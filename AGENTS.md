# AGENTS.md

Project guidance for coding/design assistants working in `pottery-wheel-tools`.

## Inheritance
- Global standards from `../AGENTS.md` apply here.
- This file adds project-specific geometry, structure, and build rules.

## Scope
- Treat `pottery-wheel-tools/` as the project root.
- Keep `core_mount_system/` stable; new designs should usually go under `attachments/`.

## Canonical Mount References
- Canonical clamp profile: `core_mount_system/c_clamp/v1/c_clamp_profile_topref_v1.scad`
- Canonical sweep reference: `core_mount_system/c_clamp/v1/c_clamp_sweep_reference_v1.scad`
- Do **not** re-derive clamp geometry from STL when profile points already exist.

## Reusable Mount Components
- `c_clamp` is an active, reusable mount component (not legacy).
- `saddle` is the active inside-drop reusable mount component.
- build123d canonical implementation paths:
  - `cad/build123d/attachments/c_clamp/v1/c_clamp_v1.py`
  - `cad/build123d/attachments/saddle/v1/saddle_v1.py`
- Preferred builder APIs in Python:
  - `build_c_clamp(...)`
  - `build_saddle(...)`

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

## build123d Authoring Requirements
- For new Python CAD models, place files under `cad/build123d/attachments/<attachment_name>/vN/`.
- Follow `cad/build123d/CONVENTIONS.md` for script layout and UX defaults.
- Keep a `Primary knobs` section at the top of each script for high-impact tuning only.
- Standard run toggles (same names across scripts):
  - `USE_HEAD_CONFIG`
  - `HEAD_PREVIEW`
  - `HEAD_EXPORT`
  - `HEAD_OUTPUT`
- Standard CLI flags (same names across scripts):
  - `--preview`
  - `--export`
  - `--output`
- No-arg run (VS Code Run button) should default to preview mode.
- Preview should skip STL export unless export is explicitly enabled.
- Each build123d part should include concise preview/export commands in either part notes or `cad/build123d/README.md`.

## Experiments
- Place unfinished work in `experiments/`.
- Promote only validated designs into versioned `attachments/` folders.
