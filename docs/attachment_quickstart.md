# Attachment Quickstart

This is the fastest path to start a new attachment with the C-clamp mount system.

## 1. Scaffold a new attachment

```bash
./scripts/new_attachment.sh <attachment_name> [version]
```

Examples:

```bash
./scripts/new_attachment.sh needle_tool_holder
./scripts/new_attachment.sh camera_mount v2
```

This creates:
- `attachments/<name>/<version>/<name>_<version>.scad`
- `attachments/<name>/<version>/notes.md`

## 2. Edit the SCAD parameters first
- `render_holder_only`
- `sweep_angle`, `radius`
- pad/platform dimensions
- attachment placement (`attach_angle`, radial offset, top offset)
- attachment dimensions and tilt

## 3. Run checks

```bash
make check
```

## 4. Fast fit sample print (attachment-only)
Set `render_holder_only = true` in your SCAD, then export/print a quick sample.

## 5. Full export

```bash
make all
```

## 6. Document results
Record fit, clearances, print settings, and next changes in `notes.md`.

---

## Non-negotiables
- Use canonical clamp profile:
  - `core_mount_system/c_clamp/v1/c_clamp_profile_topref_v1.scad`
- Keep top-reference anchor (`max Y = 0`) intact unless intentionally changing core mount geometry.
- Avoid re-deriving profile from STL when point data exists.
