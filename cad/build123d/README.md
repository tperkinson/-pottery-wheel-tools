# build123d Migration Slice

This folder holds build123d ports of attachment models.

build123d currently requires Python `<3.14`.

Project conventions for future build123d files:
- `cad/build123d/CONVENTIONS.md`
- `cad/build123d/templates/part_template.py`

## Quick start

1. Create and activate a local environment:

```sh
python3.13 -m venv .venv-b123d
source .venv-b123d/bin/activate
python -m pip install -r cad/build123d/requirements.txt
```

2. Export the pottery stamp STL:

```sh
make PYTHON_B123D=.venv-b123d/bin/python stamp_tlp_b123d
```

Output path:

- `build/pottery_stamp_tlp_v8_b123d.stl`

## Explore / view the model

- Fastest (already in your toolchain): open the STL in OpenSCAD

```sh
openscad build/pottery_stamp_tlp_v8_b123d.stl
```

- For better mesh inspection: open in your slicer (OrcaSlicer, PrusaSlicer, Cura) or MeshLab.

## Direct script usage

```sh
python cad/build123d/attachments/pottery_stamp/v8/pottery_stamp_tlp_v8.py \
  --output build/pottery_stamp_tlp_v8_b123d.stl \
  --text TLP \
  --scale-factor 0.6
```

## VS Code preview mode

Use this while iterating parameters to preview without exporting STL each run:

```sh
python cad/build123d/attachments/pottery_stamp/v8/pottery_stamp_tlp_v8.py --preview
```

If you run the file with no args (for example VS Code "Run Python File"), it now defaults to preview mode.
To toggle one-click STL export for no-arg runs, set `PRIMARY_EXPORT_ON_RUN` in:
`cad/build123d/attachments/pottery_stamp/v8/pottery_stamp_tlp_v8.py`.

Preview and export in one run:

```sh
python cad/build123d/attachments/pottery_stamp/v8/pottery_stamp_tlp_v8.py --preview --export
```
