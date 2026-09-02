CLI Reference
=============

AquaPose exposes all pipeline operations through a single ``aquapose`` command.
The ``--project`` / ``-p`` option is a **top-level** argument placed *before* the
subcommand — it selects the project whose ``config.yaml`` is loaded for every
subsequent operation::

    aquapose -p myproject <subcommand> [options]

See also: :doc:`API module reference <../api/cli>`

.. _cli-reference-auto:

Command Reference
-----------------

.. click:: aquapose.cli:cli
   :prog: aquapose
   :nested: full

.. _cli-examples:

Worked Examples
---------------

Root commands
~~~~~~~~~~~~~

**run** — Execute the full pipeline (or up to ``--max-chunks`` chunks):

.. code-block:: bash

    # Run all available video chunks
    aquapose -p myproject run

    # Run at most 6 chunks (useful for a quick smoke-test)
    aquapose -p myproject run --max-chunks 6

    # Run in diagnostic mode with verbose output
    aquapose -p myproject run -m diagnostic -v

    # Override a config key inline without editing config.yaml
    aquapose -p myproject run --set detection.conf_threshold=0.4

    # Stop after pose estimation (skip tracking and later stages)
    aquapose -p myproject run --stop-after pose

**init** — Scaffold a new project directory with a starter ``config.yaml``:

.. code-block:: bash

    # Create ~/aquapose/projects/myproject/ with default config
    aquapose init myproject

    # Include a synthetic section in the generated config
    aquapose init myproject --synthetic

**eval** — Print a summary report for a completed run:

.. code-block:: bash

    # Evaluate the most recent run
    aquapose -p myproject eval

    # Evaluate a specific run by ID and output JSON
    aquapose -p myproject eval run_20260101_120000 --report json

**eval-compare** — Compare two runs side-by-side:

.. code-block:: bash

    aquapose -p myproject eval-compare run_20260101_120000 run_20260102_090000

**tune** — Hyperparameter sweep over config fields:

.. code-block:: bash

    aquapose -p myproject tune

**viz** — Visualise pipeline outputs (detections, tracks, reconstructions):

.. code-block:: bash

    aquapose -p myproject viz

**stitch** — Stitch per-chunk HDF5 outputs into a single file:

.. code-block:: bash

    aquapose -p myproject stitch

**smooth-z** — Post-process z-coordinates with a Kalman smoother:

.. code-block:: bash

    aquapose -p myproject smooth-z

Subgroup: ``data``
~~~~~~~~~~~~~~~~~~

Manage training data stores (OBB and pose sample stores).

.. code-block:: bash

    # Import labelled samples from a Label Studio export
    aquapose -p myproject data import --store obb --input labels.json

    # List all samples in the pose store
    aquapose -p myproject data list --store pose

    # Show store status (counts, class distribution)
    aquapose -p myproject data status --store obb

    # Exclude a problematic sample by ID
    aquapose -p myproject data exclude --store obb --id 42

Subgroup: ``train``
~~~~~~~~~~~~~~~~~~~

Train oriented bounding-box, segmentation, and pose models.

.. code-block:: bash

    # Train the OBB detector
    aquapose -p myproject train obb

    # Train the pose model with a custom epoch count
    aquapose -p myproject train pose --epochs 100

    # Compare two training runs
    aquapose -p myproject train compare run_a run_b

Subgroup: ``prep``
~~~~~~~~~~~~~~~~~~

Compute derived configuration values (keypoint t-values, lookup tables).

.. code-block:: bash

    # Compute keypoint t-values from COCO annotations and write to config
    aquapose -p myproject prep calibrate-keypoints --annotations annotations.json

    # Pre-generate forward and inverse refractive lookup tables
    aquapose -p myproject prep generate-luts

Subgroup: ``pseudo-label``
~~~~~~~~~~~~~~~~~~~~~~~~~~

Generate pseudo-labels from diagnostic pipeline caches.

.. code-block:: bash

    # Generate pseudo-labels for the most recent run
    aquapose -p myproject pseudo-label generate

    # Mine hard negatives from a specific run
    aquapose -p myproject pseudo-label mine-hard run_20260101_120000

    # Select confident pseudo-labels above a threshold
    aquapose -p myproject pseudo-label select

Subgroup: ``reid``
~~~~~~~~~~~~~~~~~~

Fish re-identification: embed detections, mine crops, fine-tune, repair.

.. code-block:: bash

    # Embed detections for the most recent run
    aquapose -p myproject reid embed

    # Mine crops for fine-tuning
    aquapose -p myproject reid mine-crops

    # Fine-tune the re-ID projection head
    aquapose -p myproject reid fine-tune

    # Repair identity assignments in a completed run
    aquapose -p myproject reid repair
