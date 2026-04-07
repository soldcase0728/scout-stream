import pytest
import numpy as np

from processing.landmark_contract import LandmarkFrame, LandmarkPoint, LandmarkTimeSeries


def make_landmark_point(x: float, y: float, z: float, vis: float = 0.9) -> LandmarkPoint:
    return LandmarkPoint(x=x, y=y, z=z, visibility=vis)


def make_frame(
    frame_index: int,
    pelvis_y: float = 0.6,
    shoulder_y: float = 0.4,
    hip_rotation: float = 0.0,
    shoulder_rotation: float = 0.0,
) -> LandmarkFrame:
    """Create a synthetic frame with controllable parameters.

    pelvis_y / shoulder_y: vertical positions (lower = higher in MediaPipe)
    hip_rotation / shoulder_rotation: lateral offsets to simulate rotation
    """
    return LandmarkFrame(
        frame_index=frame_index,
        left_hip=make_landmark_point(-0.1 + hip_rotation, pelvis_y, 0.0),
        right_hip=make_landmark_point(0.1 + hip_rotation, pelvis_y, 0.0),
        left_shoulder=make_landmark_point(-0.15 + shoulder_rotation, shoulder_y, 0.0),
        right_shoulder=make_landmark_point(0.15 + shoulder_rotation, shoulder_y, 0.0),
        left_ankle=make_landmark_point(-0.1, 0.9, 0.0),
        right_ankle=make_landmark_point(0.1, 0.9, 0.0),
        left_heel=make_landmark_point(-0.12, 0.92, -0.02),
        right_heel=make_landmark_point(0.12, 0.92, -0.02),
        left_foot_index=make_landmark_point(-0.12, 0.92, 0.05),
        right_foot_index=make_landmark_point(0.12, 0.92, 0.05),
        left_wrist=make_landmark_point(-0.2, 0.5, 0.0),
        right_wrist=make_landmark_point(0.0, 0.5, 0.0),
        left_knee=make_landmark_point(-0.1, 0.75, 0.0),
        right_knee=make_landmark_point(0.1, 0.75, 0.0),
    )


@pytest.fixture
def stable_series() -> LandmarkTimeSeries:
    """Series with minimal movement - good for testing start detection."""
    frames = [make_frame(i) for i in range(30)]
    return LandmarkTimeSeries(frames=frames, frame_rate=30.0)


@pytest.fixture
def swing_series() -> LandmarkTimeSeries:
    """Series simulating a swing: stable → movement → delivery → contact."""
    frames = []
    for i in range(60):
        if i < 15:
            # Stable stance
            f = make_frame(i)
        elif i < 30:
            # Movement / gather phase
            progress = (i - 15) / 15
            f = make_frame(
                i,
                pelvis_y=0.6 - progress * 0.02,
                hip_rotation=progress * 0.03,
            )
        elif i < 45:
            # Launch / delivery phase - hips open, then shoulders
            progress = (i - 30) / 15
            f = make_frame(
                i,
                pelvis_y=0.58,
                hip_rotation=0.03 + progress * 0.08,
                shoulder_rotation=progress * 0.06,
            )
        else:
            # Contact / follow-through
            progress = (i - 45) / 15
            f = make_frame(
                i,
                pelvis_y=0.56 + progress * 0.03,
                hip_rotation=0.11 + progress * 0.02,
                shoulder_rotation=0.06 + progress * 0.05,
            )
        frames.append(f)
    return LandmarkTimeSeries(frames=frames, frame_rate=30.0)
