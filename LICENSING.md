# Licensing

AquaPose is licensed under the **[GNU Affero General Public License v3.0 or
later (AGPL-3.0-or-later)](LICENSE)**.

## This is a constraint, not a preference

AGPL-3.0-or-later was not chosen because it was the ideal license for a
research codebase — it is the license that AquaPose's dependency chain
forces on it. Two of AquaPose's core dependencies are themselves copyleft:

- **[Ultralytics](https://github.com/ultralytics/ultralytics)** (AGPL-3.0) —
  the detection and pose estimation backbone. Every YOLO-based stage in the
  pipeline (bounding-box detection, pose keypoint estimation) depends on it.
- **[python-igraph](https://github.com/igraph/python-igraph) /
  [leidenalg](https://github.com/vtraag/leidenalg)** (GPL-2.0-or-later) — the
  cross-camera association layer's community-detection backend.

Under the terms of the AGPL and GPL, a work that links against or otherwise
combines with AGPL/GPL-licensed code must itself be distributed under a
compatible copyleft license. AquaPose cannot be MIT (or any other permissive
license) while it depends on Ultralytics and leidenalg/igraph.

## What this means for you

If you build on AquaPose — as a library, a fork, or a service that exposes
its functionality over a network — your derivative work must also be
licensed AGPL-3.0-or-later (or a compatible license), and if you run it as a
network service, you must make the complete corresponding source available
to users of that service. This is the AGPL's defining difference from the
plain GPL: the copyleft obligation extends to network use, not just
distribution. Read the full text in [LICENSE](LICENSE) for the binding
terms; this document is background, not a substitute for it.

## Alternatives we considered and rejected

- **An Ultralytics Enterprise License.** This would relax the AGPL
  obligation coming from Ultralytics specifically, but it costs money and
  does nothing about the GPL-2.0-or-later obligation from python-igraph and
  leidenalg. It would not have let AquaPose stay permissively licensed.
- **Replacing Ultralytics to preserve an MIT license.** Ultralytics is not
  an interchangeable utility dependency — it *is* AquaPose's detection and
  pose estimation pipeline. Replacing it would mean re-implementing and
  re-validating the core of the system, not swapping a library.

Neither alternative was viable, so AGPL-3.0-or-later is the license going
forward.

## The MIT-to-AGPL boundary

Releases up to and including **v1.1.1** were published under the MIT
License, and that grant stands — it is not being revoked or reinterpreted.
Starting with **v1.2.0**, AquaPose is licensed AGPL-3.0-or-later. We are not
taking a position here on whether the earlier MIT releases were already
out of compliance given the AGPL/GPL dependency chain in effect at the
time; we are simply recording the boundary going forward.

The v1.1.0 and v1.1.1 releases are **not** being yanked from PyPI. They
remain available under their original MIT terms.
