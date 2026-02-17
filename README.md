# Pottery Wheel Tools

This repo is organized as a reusable mount-platform project with versioned assets.

## Structure
- `core_mount_system/`: shared splash-pan clip and clamp geometry references.
- `core_mount_system/c_clamp/v1/`: canonical C-clamp assets for interface version 1.
- `core_mount_system/docs/`: interface rules, dimensions, and tolerances.
- `attachments/<name>/<version>/`: versioned add-ons that depend on core interface.
- `experiments/`: one-off prototypes, historical files, and scratch work.

## Naming Convention
- Files use lowercase snake-case and explicit versions, for example `phone_mount_v1.scad`.
- Stable reference geometry remains in `core_mount_system`.
- Attachment versions are immutable once released; new updates use `v2`, `v3`, etc.

## Build / Export
- A `Makefile` is provided for consistent STL exports to `build/`.
- Run `make help` to list available targets.
- Run `make check` for fast geometry compile checks.
- Initial build123d migration notes and commands:
  - `cad/build123d/README.md`

## Start New Attachment
- Scaffold a new attachment:
  - `./scripts/new_attachment.sh <attachment_name> [version]`
- Example:
  - `./scripts/new_attachment.sh camera_mount v1`
- Full guide:
  - `docs/attachment_quickstart.md`

## Design Convention
- Keep core interface geometry stable.
- Build new attachments against the core reference files.
- Promote an experiment into `attachments/` only after fit and print checks.
