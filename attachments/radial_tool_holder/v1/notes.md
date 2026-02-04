# radial_tool_holder (v1)

## Purpose
- Curved multi-compartment tool holder that follows the wheel arc and mounts with the canonical C-clamp/C-cup sweep.
- The mount flat wall is reused as the container front wall in the full assembly (no redundant parallel wall).

## Files
- `radial_tool_holder_v1.scad`
- `notes.md`

## Geometry Proposal (Pre-code)
- Holder is modeled as an annular-sector container in the local attachment frame.
- Local frame convention:
  - `+X`: radial outward
  - `+Y`: tangent
  - `+Z`: profile-up

### Parameters
- `arc_length`
- `radial_width`
- `depth`
- `wall_thickness`
- `floor_thickness`
- `compartment_count`
- `divider_thickness`
- Drain holes:
  - `enable_drain_holes`
  - `drain_hole_diameter`
  - `drain_hole_radial_offset`
  - `drain_hole_arc_offset`
- `holder_tilt_deg`
- `holder_radial_location_on_pad`
- `container_top_offset` (top-of-container height relative to clamp top)
- Shared-wall interface:
  - `shared_wall_overlap`
  - `shared_wall_height`
  - `shared_wall_blend_radius`

### Derived Math
- `centerline_radius` from mount placement (`shared_wall_radius + holder_radial_location_on_pad`)
- `arc_angle_deg = arc_length / centerline_radius * 180 / PI`
- `inner_radius = centerline_radius - radial_width / 2`
- `outer_radius = centerline_radius + radial_width / 2`
- `divider_count = max(0, compartment_count - 1)`
- Divider spacing is uniform along arc:
  - equal centerline arc-length spacing (equal angular increments)

## Final Geometry Approach
- Clamp + pad are swept from canonical profile (`c_clamp_profile_topref_v1.scad`).
- Holder geometry remains separate (linear/non-swept modules).
- `arc_length` is the controlling value for holder sweep angle (`arc_angle_deg`) and clamp sweep follows it.
- Pad is disabled by default (`show_pad = false`) to avoid a top overhang that can block tool access.
- Container is top-referenced to clamp top and drops downward by `depth`:
  - top rim at `max_profile_y + container_top_offset`
  - cavity extends downward (negative local Z)
- The shell body is built as one extrusion/difference pass:
  - includes bottom + back wall + shared front-wall merge strip
- Dividers and side walls are then added as separate modules.
- Drain holes are subtracted from the floor (one per compartment), centered per compartment with optional radial/arc offsets.

## Shared-Wall Implementation Details
- Shared wall reference is the canonical mount flat wall at `max_profile_x`.
- Shell includes a controlled merge strip (`shared_wall_overlap`) that intersects this wall for a continuous load path.
- Extra front strip can be height-limited by `shared_wall_height`.
- No separate full-height inner wall is added in the assembled model.
- `shared_wall_blend_radius` adds local thickening near the front interface.

## Assumptions Used
- Wheel/mount defaults from repo are used (`radius = 222.25 mm`, top-referenced canonical profile).
- Available mount flat-wall height is treated as ~`45.4 mm` for shared-wall validation.
- Baseline load-bearing printability target is ~`>= 3 mm` walls.

## Geometry Validity Checks / Warnings Added
- Too-thin members:
  - `wall_thickness`, `divider_thickness`, `floor_thickness`
- Impossible compartment packing:
  - `arc_length` vs wall/divider + minimum pocket length budget
  - divider spacing too tight for selected `compartment_count`
- Self-intersection risk:
  - invalid radii/angles
  - insufficient radial cavity room
  - invalid depth/floor relation
  - overlap pushing across sweep axis
- Clamp/pad interference risk:
  - holder exceeding swept span
  - excessive downward reach into clamp envelope
  - excessive overlap amount
  - optional pad overhang blocking top access
- Shared-wall validity:
  - invalid `shared_wall_overlap`
  - invalid `shared_wall_height`
  - inner radius drifting outside mount-wall interface
- Drain-hole validity:
  - diameter <= 0
  - radial offset pushing hole into front/back walls
  - arc offset pushing hole outside compartment opening

## Tuning Order
1. `container_top_offset` and `depth` (how far pockets drop from clamp top).
2. `holder_radial_location_on_pad` and `radial_width` (envelope and wall contact location).
3. `arc_length` (coverage along wheel arc).
4. `compartment_count` and `divider_thickness` (organization).
5. `wall_thickness` and `floor_thickness` (strength/printability).
6. `shared_wall_overlap`, `shared_wall_height`, `shared_wall_blend_radius` (mount interface behavior).
7. `holder_tilt_deg` and optional gusset parameters (ergonomics/stiffness).
8. `drain_hole_diameter`, then `drain_hole_radial_offset` / `drain_hole_arc_offset`.

## Fit/Test Log
- Date: 2026-02-04
- Printer/material:
- Layer/nozzle:
- Fit result:
- Next adjustment:

## Release Notes
- v1:
  - Annular-sector multi-compartment holder with even divider spacing.
  - Sweep angle now follows `arc_length` and placement radius.
  - Container top anchored to clamp top with downward pocket depth control.
  - Shell-first extrusion strategy (bottom + back wall + shared front merge strip), then side walls/dividers.
  - Shared-wall interface and packing/interference warnings added.
  - Added one drain hole per compartment with diameter and center-offset controls.
