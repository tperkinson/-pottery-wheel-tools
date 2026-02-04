# costco_cup_holder (v1)

## Purpose
- Hold a red Costco Solo-style cup using a lip-capture hoop on the canonical C-clamp splash-pan mount.

## Files
- `costco_cup_holder_v1.scad`
- `notes.md`

## Geometry Proposal (Before Implementation)
- Keep clamp + pad as swept geometry from canonical profile (`max_profile_y = 0` preserved).
- Keep cup holder as linear geometry:
  - radial bridge from mount
  - circular hoop with through-hole sized to cup body
  - lip rests on hoop top edge because lip OD is larger than hole OD
- Keep the region directly under the hoop hole clear of pad geometry so the cup can drop through.
- Add mount-side gusset between bridge and hoop for load stiffness.
- Include `render_holder_only` mode for fast fit prints without clamp sweep.

## Key Parameters
- `cup_lip_diameter`
- `cup_body_diameter_below_lip`
- `ring_thickness`
- `clearance`
- `sweep_fit_mode` (`manual` / `auto_hoop_kiss`)
- `sweep_fit_diameter_mode` (`hoop_outer` / `cup_lip_exterior`)
- `holder_tilt_deg`
- `holder_radial_location_on_pad`
- `hoop_center_offset_from_mount`
- `bridge_width`, `bridge_thickness`
- `enable_mount_gusset`

## Sweep "Kiss" Calculation
- Goal: make hoop side tangent to both sweep side planes.
- Auto mode uses:
  - `R_center = attach_r + hoop_center_offset_from_mount * cos(holder_tilt_deg)`
  - `R_fit = (selected fit diameter / 2) + sweep_kiss_clearance`
  - `sweep_angle = 2 * asin(R_fit / R_center)`
- Radial placement is included through `attach_r` (driven by `holder_radial_location_on_pad`).
- `attach_angle_mode = auto_center` keeps hoop centered between sweep sides.

## Starting Assumptions (Need Measurement Validation)
- `cup_lip_diameter = 97.0` mm
- `cup_body_diameter_below_lip = 93.5` mm
- `clearance = 0.35` mm
- These are reasonable Solo-style defaults, but should be measured on your actual Costco cup.

## Measurements To Take On The Real Cup
- Lip outer diameter at the rolled rim.
- Body outer diameter about 8-12 mm below the lip.
- Optional: lip roll width/thickness if you want more precise seating margin.

## Tuning Order (First To Last)
1. `cup_body_diameter_below_lip` (primary pass-through fit).
2. `clearance` (friction vs wobble).
3. `cup_lip_diameter` (verifies lip capture margin warning).
4. `holder_radial_location_on_pad` and `hoop_center_offset_from_mount` together:
   keep the under-hoop region open while placing the cup where you want it.
5. `holder_tilt_deg` (drain/ergonomics).
6. `ring_thickness` and bridge/gusset sizes (strength only).

## Export Workflow
- Full model STL: `make cup_holder`
- Holder-only sample STL: `make cup_holder` (same target exports both)
- Outputs:
  - `build/costco_cup_holder_v1.stl`
  - `build/costco_cup_holder_v1_holder_sample.stl`

## Fit/Test Log
- Date: 2026-02-04
- Printer/material:
- Layer/nozzle:
- Fit result:
- Next adjustment:

## Release Notes
- v1:
  - Implemented lip-capture hoop holder with mount bridge + gusset.
  - Added holder-only render path for quick fit testing.
  - Parameterized cup-fit and placement controls for iterative tuning.
  - Added auto sweep-angle calculation so hoop can "kiss" both sweep boundaries.
