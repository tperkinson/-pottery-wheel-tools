# costco_cup_holder (v1, build123d)

## Purpose
- build123d representation of `attachments/costco_cup_holder/v1/costco_cup_holder_v1.scad` with matching default geometry intent.

## Files
- `cad/build123d/attachments/costco_cup_holder/v1/costco_cup_holder_v1.py`
- `attachments/costco_cup_holder/v1/notes.md`

## Quick Commands
Preview (default no STL export):

```sh
.venv-b123d/bin/python cad/build123d/attachments/costco_cup_holder/v1/costco_cup_holder_v1.py --preview
```

Export STL:

```sh
.venv-b123d/bin/python cad/build123d/attachments/costco_cup_holder/v1/costco_cup_holder_v1.py --export --output build/costco_cup_holder_v1_b123d.stl
```

Holder-only sample export:

```sh
.venv-b123d/bin/python cad/build123d/attachments/costco_cup_holder/v1/costco_cup_holder_v1.py --holder-only --export --output build/costco_cup_holder_v1_b123d_holder_only.stl
```

## Output Path
- Default STL output: `build/costco_cup_holder_v1_b123d.stl`

## Notes
- No-arg run path defaults to preview mode.
- STL export is skipped in preview-only runs unless `--export` is used.
- Clamp/pad sweep remains canonical-topref and separate from linear holder geometry.
- Ring-fit controls are unchanged from the validated fit:
  - `cup_body_diameter_below_lip = 93.5`
  - `clearance = 0.35`
  - `ring_thickness = 5.5`
- Tray/pad is fully disabled in the build123d default:
  - `show_pad: True -> False`
  - `pad_length: 56.0 -> 0.0`
  - `holder_radial_location_on_pad: 0.98 * pad_length -> 0.0`
  - holder now bonds directly from clamp outer edge to ring connector
- Connection style was changed:
  - `enable_mount_gusset`: `True -> False`
  - ring top is now flush to clamp top-reference plane
  - ring center offset is now derived from ring OD so ring near side is flush to clamp bond plane
  - near-side connector is full-height (`bridge_thickness`: `7.0 -> 14.0`)
  - connector band widened (`bridge_width`: `30.0 -> 42.0`)
  - ring overlap increased to full ring wall (`bridge_overlap_into_ring`: `4.5 -> 5.5`)
  - clamp-side overlap added for true volumetric intersection (`bridge_overlap_into_clamp = 2.0`)
- No full tray is used under the far side of the ring; support is concentrated in the near-side connector.
