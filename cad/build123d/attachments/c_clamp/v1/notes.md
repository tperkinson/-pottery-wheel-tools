# c_clamp (v1, build123d)

## Purpose
- Parameterized C-clamp mount sweep built in build123d.
- Baseline shape comes from the canonical profile, with targeted tuning for back-wall height.

## Files
- `c_clamp_v1.py`
- `notes.md`

## Primary knobs
- `PRIMARY_SWEEP_ANGLE_DEG`
- `PRIMARY_RADIUS_MM`
- `PRIMARY_PROFILE_WIDTH_MM`
- `PRIMARY_BACK_WALL_HEIGHT_MM`
- `PRIMARY_MOUTH_RELIEF_MM`
- `PRIMARY_PROFILE_RADIAL_OFFSET_MM`
- `PRIMARY_PAD_LENGTH_MM`

## Preview command
```sh
source .venv-b123d/bin/activate
python cad/build123d/attachments/c_clamp/v1/c_clamp_v1.py --preview
```

## Export command
```sh
source .venv-b123d/bin/activate
python cad/build123d/attachments/c_clamp/v1/c_clamp_v1.py --export
```

## Output path
- `build/c_clamp_v1_b123d.stl`

## Key tuning flag
- `--back-wall-height` controls the long straight back wall directly (default canonical: `45.398` mm).
