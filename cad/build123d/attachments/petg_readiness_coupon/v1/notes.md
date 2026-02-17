# petg_readiness_coupon_v1

Purpose:
- Fast PETG preflight print before long jobs.
- Single part checks:
  - First-layer adhesion/warping on a wider base.
  - Stringing (two separated towers).
  - Bridging quality (open tunnel roof).
  - Overhang behavior (step cantilever ladder).
  - Thin-wall/perimeter consistency (0.8 / 1.2 / 1.6 mm fins).

Preview command:
`cd /Users/terryperkinson/pottery3d/pottery-wheel-tools && source .venv-b123d/bin/activate && python cad/build123d/attachments/petg_readiness_coupon/v1/petg_readiness_coupon_v1.py --preview`

Export command:
`cd /Users/terryperkinson/pottery3d/pottery-wheel-tools && source .venv-b123d/bin/activate && python cad/build123d/attachments/petg_readiness_coupon/v1/petg_readiness_coupon_v1.py --export --output build/petg_readiness_coupon_v1_b123d.stl`

Output path:
- `/Users/terryperkinson/pottery3d/pottery-wheel-tools/build/petg_readiness_coupon_v1_b123d.stl`

Quick pass/fail for a long PETG print:
- Pass:
  - Base corners stay flat (no edge lifting).
  - Bridge roof is mostly straight with only light sag.
  - Stringing between towers is light wisps (easy to wipe).
  - Overhang ladder remains connected without drooped curls.
  - 1.2 mm and 1.6 mm fins are clean and vertical.
- Caution before long print:
  - Corners lifting or splitting layers.
  - Heavy bridge droop with rough underside blobs.
  - Thick string webs between towers.
  - Overhang steps collapsing.
