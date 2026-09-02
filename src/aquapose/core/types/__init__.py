"""Cross-stage shared types for AquaPose core."""

from aquapose.core.types.crop import AffineCrop, CropRegion
from aquapose.core.types.detection import Detection
from aquapose.core.types.frame_source import (
    ChunkFrameSource,
    FrameSource,
    VideoFrameSource,
)
from aquapose.core.types.midline import Midline2D
from aquapose.core.types.reconstruction import Midline3D, MidlineSet
from aquapose.core.types.video_discovery import discover_camera_videos

__all__ = [
    "AffineCrop",
    "ChunkFrameSource",
    "CropRegion",
    "Detection",
    "FrameSource",
    "Midline2D",
    "Midline3D",
    "MidlineSet",
    "VideoFrameSource",
    "discover_camera_videos",
]
