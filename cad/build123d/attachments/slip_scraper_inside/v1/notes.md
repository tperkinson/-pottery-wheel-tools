# slip_scraper_inside_v1

Modeling method:
- Curved lip scraper in XZ profile (arc-based), extruded across width.
- Lip is offset from the saddle inside wall (`reach`) and lifted (`rise`) to place the scrape zone.
- Open center drain path is preserved by using side support ribs instead of a full center bridge.

Preview command (full assembly):
`cd /Users/terryperkinson/pottery3d/pottery-wheel-tools && source .venv-b123d/bin/activate && python cad/build123d/attachments/slip_scraper_inside/v1/slip_scraper_inside_v1.py --preview`

Export command (full assembly):
`cd /Users/terryperkinson/pottery3d/pottery-wheel-tools && source .venv-b123d/bin/activate && python cad/build123d/attachments/slip_scraper_inside/v1/slip_scraper_inside_v1.py --export --output build/slip_scraper_inside_v1_b123d.stl`

Export command (mount-only mode):
`cd /Users/terryperkinson/pottery3d/pottery-wheel-tools && source .venv-b123d/bin/activate && python cad/build123d/attachments/slip_scraper_inside/v1/slip_scraper_inside_v1.py --mount-only --export --output build/slip_scraper_inside_v1_mount_only_b123d.stl`

Output paths:
- `/Users/terryperkinson/pottery3d/pottery-wheel-tools/build/slip_scraper_inside_v1_b123d.stl`
- `/Users/terryperkinson/pottery3d/pottery-wheel-tools/build/slip_scraper_inside_v1_mount_only_b123d.stl`

Tuning order:
1. Mount fit in `saddle_v1.py` (`PRIMARY_PAN_WALL_THICKNESS_MM`, `PRIMARY_FIT_CLEARANCE_MM`, `PRIMARY_CAPTURE_DEPTH_MM`, `PRIMARY_INSIDE_DROP_GAP_MM`)
2. `PRIMARY_SCRAPER_REACH_MM` (lip center radial offset from saddle)
3. `PRIMARY_SCRAPER_RISE_MM` (lip center vertical rise)
4. `PRIMARY_SCRAPER_LIP_RADIUS_MM`
5. `PRIMARY_SCRAPER_DRAIN_GAP_MM`
6. `PRIMARY_SCRAPER_WIDTH_MM`
7. `PRIMARY_SCRAPER_EDGE_RADIUS_MM`
8. `PRIMARY_GUSSET_THICKNESS_MM`

Default changes in this pass:
- `PRIMARY_SCRAPER_REACH_MM`: `40.0 -> 15.0`
- Added:
  - `PRIMARY_SCRAPER_RISE_MM = 15.0`
  - `PRIMARY_SCRAPER_LIP_RADIUS_MM = 14.0`
  - `PRIMARY_SCRAPER_DRAIN_GAP_MM = 6.0`
