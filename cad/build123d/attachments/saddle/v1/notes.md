# saddle_v1

Modeling method:
- Single canonical C-clamp-derived saddle profile in 2D (XZ): same top/back behavior as C-clamp, then straight inside drop from the top curve tip, swept around pan radius.
- Includes optional inside square top cap to mirror the outside flat-top style (`PRIMARY_INSIDE_TOP_SQUARE_ENABLE`).
- Includes optional outside top relief cut to remove non-structural square mass (`PRIMARY_OUTSIDE_TOP_RELIEF_ENABLE`).

Preview command:
`cd /Users/terryperkinson/pottery3d/pottery-wheel-tools && source .venv-b123d/bin/activate && python cad/build123d/attachments/saddle/v1/saddle_v1.py --preview`

Export command:
`cd /Users/terryperkinson/pottery3d/pottery-wheel-tools && source .venv-b123d/bin/activate && python cad/build123d/attachments/saddle/v1/saddle_v1.py --export --output build/saddle_v1_b123d.stl`

Output path:
`/Users/terryperkinson/pottery3d/pottery-wheel-tools/build/saddle_v1_b123d.stl`

Tuning order:
1. `PRIMARY_PAN_WALL_THICKNESS_MM`
2. `PRIMARY_FIT_CLEARANCE_MM`
3. `PRIMARY_CAPTURE_DEPTH_MM`
4. `PRIMARY_SWEEP_RADIUS_MM`
5. `PRIMARY_MOUNT_WALL_THICKNESS_MM`
6. `PRIMARY_MOUNT_HEIGHT_MM`
7. `PRIMARY_INSIDE_DROP_GAP_MM` (or CLI `--inside-drop-gap`, default `4.5`)
8. `PRIMARY_INSIDE_DROP_TOP_Z_MM`
9. `PRIMARY_INSIDE_TOP_SQUARE_ENABLE`
10. `PRIMARY_INSIDE_TOP_SQUARE_WIDTH_MM`
11. `PRIMARY_OUTSIDE_TOP_RELIEF_ENABLE`
12. `PRIMARY_OUTSIDE_TOP_RELIEF_WIDTH_MM`
13. `PRIMARY_OUTSIDE_TOP_RELIEF_DEPTH_MM`
14. `PRIMARY_DETENT_ENABLE` + `PRIMARY_DETENT_HEIGHT_MM`

Square-top controls:
- Enable/disable: `--inside-top-square` / `--no-inside-top-square`
- Width: `--inside-top-square-width <mm>`

Outside top relief controls:
- Enable/disable: `--outside-top-relief` / `--no-outside-top-relief`
- Width: `--outside-top-relief-width <mm>`
- Depth: `--outside-top-relief-depth <mm>`

Default: `PRIMARY_DETENT_ENABLE = False` for clean profile matching during fit iteration.

Canonical C-clamp reference used for top rim seat:
- top span: `13.0363 mm`
- mouth gap: `5.4901 mm`
- lower arc center X: `0.4356 mm`
- lower arc center depth from top: `15.0017 mm`
- lower arc radius: `9.5255 mm`
