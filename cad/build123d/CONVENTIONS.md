# build123d Conventions

Use this file as the required pattern for new build123d scripts in this repo.

## Goals
- Fast preview loop in VS Code.
- Consistent toggle names and CLI flags across all parts.
- High-impact tuning values easy to find at top of file.

## Required script structure
1. Imports.
2. `Primary knobs` block at top (`PRIMARY_*` constants only for big tuning values).
3. Runtime toggle block with exact names:
   - `USE_HEAD_CONFIG`
   - `HEAD_PREVIEW`
   - `HEAD_EXPORT`
   - `HEAD_OUTPUT`
4. Parameter dataclass with grouped sections:
   - Quick Tuning
   - Strength / Printability
   - Advanced Controls
   - Derived values (if needed)
5. `parse_args()` with exact flag names:
   - `--preview`
   - `--export`
   - `--output`
6. `preview_part()` helper using `ocp_vscode.show`.
7. `main()` that:
   - Defaults no-arg run to preview mode.
   - Skips STL export in preview-only runs.
   - Writes STL when export is enabled.

## Runtime behavior standard
- VS Code no-arg run should preview by default.
- Export should occur when:
  - `--export` is passed, or
  - head config is enabled and `HEAD_EXPORT=True`.
- STL output should default to `build/<part_name>_b123d.stl`.

## Ease-of-use requirement
- Every new part must include quick commands in notes/README:
  - Preview command
  - Export command
  - Output STL path

## Starter template
- Start from:
  - `cad/build123d/templates/part_template.py`
