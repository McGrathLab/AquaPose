# AquaPose

[![tests](https://img.shields.io/github/actions/workflow/status/McGrathLab/AquaPose/test.yml?branch=main)](https://github.com/McGrathLab/AquaPose/actions/workflows/test.yml)
[![docs](https://img.shields.io/readthedocs/aquapose/latest)](https://aquapose.readthedocs.io/en/latest/)
[![coverage](https://img.shields.io/codecov/c/github/McGrathLab/AquaPose/main)](https://codecov.io/gh/McGrathLab/AquaPose)
[![python](https://img.shields.io/pypi/pyversions/aquapose)](https://pypi.org/project/aquapose/)
[![pypi](https://img.shields.io/pypi/v/aquapose)](https://pypi.org/project/aquapose/)
[![license](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue)](https://github.com/McGrathLab/AquaPose/blob/main/LICENSE)

Measuring 3D fish posture and kinematics in a water tank is hard because the
air-water interface refracts every camera ray, so ordinary multi-view
triangulation is systematically wrong. AquaPose corrects for that: it takes
synchronized multi-view video from a 12-camera aquarium rig and a refractive
calibration and reconstructs per-fish 3D midlines across frames —
arc-length-sampled anatomical keypoints triangulated and optionally
spline-fitted — producing dense 3D trajectories and midline kinematics. It is
built for behavioral and neuroscience researchers running multi-camera
aquarium rigs who have video plus a calibration and want quantitative 3D
posture out, as used for cichlid behavioral research.

## Pipeline

AquaPose processes multi-view video through a 5-stage pipeline:

1. **Detection** — YOLO-based fish detection (standard or oriented bounding boxes)
2. **Tracking** — Per-camera 2D temporal tracking via OC-SORT
3. **Association** — Cross-camera tracklet association using ray-ray geometry and Leiden clustering
4. **Midline** — 2D midline extraction via YOLO-seg or YOLO-pose backends
5. **Reconstruction** — DLT triangulation of 2D midlines into 3D B-spline midlines

Long videos are processed in fixed-size temporal chunks with identity continuity across chunk boundaries.

## Quick Start

```bash
pip install aquapose
```

PyTorch is not pinned by this install; see the
[Installation](https://aquapose.readthedocs.io/en/latest/getting-started/installation.html)
page for the platform-specific PyTorch step before running the pipeline.

```bash
# Initialize a project
aquapose init-config my_project

# Run the pipeline
aquapose run --config path/to/config.yaml
```

To see it run end to end against real data, follow the
[Tutorial](https://aquapose.readthedocs.io/en/latest/getting-started/tutorial.html),
which walks a full pipeline run against the published tutorial dataset
([`10.5281/zenodo.22264079`](https://zenodo.org/records/22264079)).

## Documentation

Full documentation is at [aquapose.readthedocs.io](https://aquapose.readthedocs.io/en/latest/):

- [Installation](https://aquapose.readthedocs.io/en/latest/getting-started/installation.html)
- [Concepts](https://aquapose.readthedocs.io/en/latest/getting-started/concepts.html)
- [Tutorial](https://aquapose.readthedocs.io/en/latest/getting-started/tutorial.html)
- [API reference](https://aquapose.readthedocs.io/en/latest/api/index.html)

## Citation

If you use AquaPose in your research, please cite the software via
[CITATION.cff](https://github.com/McGrathLab/AquaPose/blob/main/CITATION.cff)
or GitHub's "Cite this repository" button on the repository page. This is
distinct from citing the tutorial dataset
([`10.5281/zenodo.22264079`](https://zenodo.org/records/22264079)): cite the
software when you mean the AquaPose codebase, and cite the dataset when you
mean the sample data it ships with.

## License

AquaPose is licensed under
[AGPL-3.0-or-later](https://github.com/McGrathLab/AquaPose/blob/main/LICENSE).
See
[LICENSING.md](https://github.com/McGrathLab/AquaPose/blob/main/LICENSING.md)
for why.
