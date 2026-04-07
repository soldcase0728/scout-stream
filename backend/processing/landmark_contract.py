"""Normalized landmark contract.

This is the interface boundary between the motion extraction layer
(MediaPipe / FreeMoCap) and our softball-specific analysis pipeline.
Everything downstream depends only on this contract, not on upstream internals.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


# MediaPipe Pose landmark indices we need
LANDMARK_INDICES = {
    "left_hip": 23,
    "right_hip": 24,
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_ankle": 27,
    "right_ankle": 28,
    "left_heel": 29,
    "right_heel": 30,
    "left_foot_index": 31,
    "right_foot_index": 32,
    "left_wrist": 15,
    "right_wrist": 16,
    "left_knee": 25,
    "right_knee": 26,
}


@dataclass
class LandmarkPoint:
    x: float
    y: float
    z: float
    visibility: float = 0.0


@dataclass
class LandmarkFrame:
    """All required landmarks for a single frame."""

    frame_index: int
    left_hip: LandmarkPoint = field(default_factory=lambda: LandmarkPoint(0, 0, 0))
    right_hip: LandmarkPoint = field(default_factory=lambda: LandmarkPoint(0, 0, 0))
    left_shoulder: LandmarkPoint = field(default_factory=lambda: LandmarkPoint(0, 0, 0))
    right_shoulder: LandmarkPoint = field(default_factory=lambda: LandmarkPoint(0, 0, 0))
    left_ankle: LandmarkPoint = field(default_factory=lambda: LandmarkPoint(0, 0, 0))
    right_ankle: LandmarkPoint = field(default_factory=lambda: LandmarkPoint(0, 0, 0))
    left_heel: LandmarkPoint = field(default_factory=lambda: LandmarkPoint(0, 0, 0))
    right_heel: LandmarkPoint = field(default_factory=lambda: LandmarkPoint(0, 0, 0))
    left_foot_index: LandmarkPoint = field(default_factory=lambda: LandmarkPoint(0, 0, 0))
    right_foot_index: LandmarkPoint = field(default_factory=lambda: LandmarkPoint(0, 0, 0))
    left_wrist: LandmarkPoint = field(default_factory=lambda: LandmarkPoint(0, 0, 0))
    right_wrist: LandmarkPoint = field(default_factory=lambda: LandmarkPoint(0, 0, 0))
    left_knee: LandmarkPoint = field(default_factory=lambda: LandmarkPoint(0, 0, 0))
    right_knee: LandmarkPoint = field(default_factory=lambda: LandmarkPoint(0, 0, 0))

    def point_as_array(self, name: str) -> np.ndarray:
        pt: LandmarkPoint = getattr(self, name)
        return np.array([pt.x, pt.y, pt.z])

    def pelvis_midpoint(self) -> np.ndarray:
        return (self.point_as_array("left_hip") + self.point_as_array("right_hip")) / 2

    def shoulder_midpoint(self) -> np.ndarray:
        return (self.point_as_array("left_shoulder") + self.point_as_array("right_shoulder")) / 2

    def min_visibility(self) -> float:
        return min(
            self.left_hip.visibility,
            self.right_hip.visibility,
            self.left_shoulder.visibility,
            self.right_shoulder.visibility,
        )


@dataclass
class LandmarkTimeSeries:
    """Full landmark sequence for one swing video."""

    frames: list[LandmarkFrame]
    frame_rate: float = 30.0
    source: str = "mediapipe"
    pipeline_version: str = "0.1.0"

    @property
    def num_frames(self) -> int:
        return len(self.frames)

    def mean_visibility(self) -> float:
        if not self.frames:
            return 0.0
        return sum(f.min_visibility() for f in self.frames) / len(self.frames)
