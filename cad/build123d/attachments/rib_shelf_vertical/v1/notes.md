# rib_shelf_vertical (v1, build123d)

## Purpose
- Radial shelf for pottery ribs stored vertically in 7 loose-drop lanes.
- Mixed rib lane widths progress small -> large from inner radius -> outer radius.
- Open-front slot field without floor channels/slots for easier clean-out.
- No bottom gusset/support web in v1; strength comes from clamp/tray overlap.
- First and last rib lanes are bounded by full-height walls (all lanes usable).
- Wall heights ramp from inside to outside using `PRIMARY_INNER_WALL_HEIGHT_MM` -> `PRIMARY_OUTER_WALL_HEIGHT_MM`.
- Wall lengths ramp from inside to outside using `PRIMARY_INNER_WALL_LENGTH_MM` -> `PRIMARY_OUTER_WALL_LENGTH_MM`.

## Files
- `rib_shelf_vertical_v1.py`
- `notes.md`

## Preview command
```sh
source .venv-b123d/bin/activate
python cad/build123d/attachments/rib_shelf_vertical/v1/rib_shelf_vertical_v1.py --preview
```

## Export command
```sh
source .venv-b123d/bin/activate
python cad/build123d/attachments/rib_shelf_vertical/v1/rib_shelf_vertical_v1.py --export
```

## Output path
- `build/rib_shelf_vertical_v1_b123d.stl`

## First 5 parameters to tune
1. `PRIMARY_SLOT_WIDTHS_MM`
2. `PRIMARY_ARC_LENGTH_MM`
3. `PRIMARY_MOUNT_OVERLAP_MM`
4. `PRIMARY_INNER_WALL_LENGTH_MM`
5. `PRIMARY_OUTER_WALL_LENGTH_MM`

## Print/usage notes
- v1 defaults target `PRIMARY_MATERIAL = "PLA"` with a `0.4 mm` nozzle.
- Intended install location is `PRIMARY_MOUNT_CLOCK_POSITION = 4` (user at 6 o'clock).
- Clamp sweep is auto-calculated from tray arc span (`PRIMARY_ARC_LENGTH_MM`) plus a small support margin.
- Guardrails in script print warnings for slot overlap, wall thinness, pitch feasibility, and trapped-water risk.
