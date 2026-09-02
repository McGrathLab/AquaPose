# Installation

This page is for **users** who want to run AquaPose on their own data or the
tutorial dataset. If you want to develop AquaPose itself — run its test suite,
lint it, or build these docs — see [Contributing](../contributing.md) for the
`hatch`-based developer setup instead; the steps below do not duplicate it.

## Install AquaPose

```bash
# Install the latest release from PyPI
pip install aquapose
```

```{note}
AquaPose is not yet published on PyPI. Publication is planned as part of a
follow-up documentation phase and should land shortly after this page does.
Until then, install directly from the GitHub repository:

    pip install git+https://github.com/McGrathLab/AquaPose.git

If `pip install aquapose` resolves to a different, unrelated package on PyPI
before the real release lands, do not trust it — that is not this project.
```

## Install PyTorch for your platform

AquaPose does not pin a specific PyTorch build. Instead, go to
<https://pytorch.org/get-started/locally/> and select your operating system,
package manager, and CUDA version (or CPU-only, if you have no NVIDIA GPU).
The selector gives you the exact `pip install torch ...` command for your
machine — running that command gets you a build of PyTorch with a CUDA
version that actually matches your installed driver, which a hardcoded
version pin in AquaPose could never guarantee.

## Verify the install

```bash
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
```

- If `torch.cuda.is_available()` prints `True`, your GPU is visible to
  PyTorch and the pipeline will run on it.
- If it prints `False`, PyTorch installed successfully but has no working
  CUDA support. The reference tutorial run is a GPU workload (see
  Prerequisites below), so you should reinstall PyTorch using the correct
  command from the pytorch.org selector before continuing.

## Prerequisites

Beyond a working `aquapose` import, three things determine whether your
first run actually succeeds:

- **`ffmpeg` on `PATH`.** `aquapose viz` shells out to `ffmpeg` to export
  MP4 animations. Install it via your OS package manager (e.g.
  `apt install ffmpeg`, `brew install ffmpeg`, or the
  [official builds](https://ffmpeg.org/download.html) on Windows) and confirm
  it resolves with `ffmpeg -version`.
- **Disk headroom.** Budget roughly **600 MB** free for the refractive
  lookup tables (LUTs) that `aquapose prep generate-luts` generates on first
  use — they are derived from your calibration and are not shipped with
  AquaPose or with any dataset. If you skip this step, the pipeline
  fails fast with a `FileNotFoundError: LUTs not found` error rather than
  silently producing wrong results. Add **215 MB** on top of that if you are
  working through the tutorial dataset.
- **A CUDA GPU.** AquaPose's detection, pose, and reconstruction stages are
  GPU workloads. The reference tutorial run fit comfortably in **6.4 GB** of
  GPU memory on a **GTX 1660 SUPER**, which is a reasonable practical floor
  for the GPU you use.

## Troubleshooting

**`nvrtc: error: failed to open libnvrtc-builtins.so`**

This means your installed PyTorch build and your NVIDIA driver disagree on
CUDA version. Reinstall PyTorch using the command from the
[pytorch.org selector](https://pytorch.org/get-started/locally/) that
matches your actual driver's CUDA version — do not assume the default
selector choice is correct if you know your driver is older or newer.

**`ffmpeg: command not found` / `FileNotFoundError` from `aquapose viz`**

`ffmpeg` is not on `PATH`. Install it (see Prerequisites above) and restart
your shell so the updated `PATH` takes effect.

## Next steps

Once `aquapose` imports and `torch.cuda.is_available()` reports the status
you expect, you're ready to move on. The rest of the Getting Started section
covers what the pipeline actually computes and walks through a full run on
the published tutorial dataset — return to the [Getting Started](index.md)
landing page to continue.

For the full set of `aquapose` subcommands and options, see the
[CLI Reference](../reference/cli.rst); for every configuration field, see the
[Config Reference](../reference/config.md).
