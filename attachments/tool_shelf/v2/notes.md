# tool_shelf (v2)

## Purpose
- build123d migration of `attachments/tool_shelf/v1/tool_shelf_v1.scad` with matching v1 geometry intent and defaults.

## Files
- `cad/build123d/attachments/tool_shelf/v2/tool_shelf_v2.py`
- `attachments/tool_shelf/v2/notes.md`

## Quick Commands
Preview (default no STL export):

```sh
.venv-b123d/bin/python cad/build123d/attachments/tool_shelf/v2/tool_shelf_v2.py --preview
```

Export STL:

```sh
.venv-b123d/bin/python cad/build123d/attachments/tool_shelf/v2/tool_shelf_v2.py --export --output build/tool_shelf_v2_b123d.stl
```

Fast holder-only sample export:

```sh
.venv-b123d/bin/python cad/build123d/attachments/tool_shelf/v2/tool_shelf_v2.py --holder-only --export --output build/tool_shelf_v2_b123d_holder_only.stl
```

## Output Path
- Default STL output: `build/tool_shelf_v2_b123d.stl`

## Notes
- No-arg run path defaults to preview mode (`--preview` behavior).
- STL export is skipped in preview-only runs unless `--export` is also enabled.
- Clamp/pad sweep remains driven by canonical `core_mount_system/c_clamp/v1/c_clamp_profile_topref_v1.scad`.
