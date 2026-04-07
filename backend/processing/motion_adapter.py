"""Motion extraction adapter.

MVP uses MediaPipe Pose directly for single-camera processing.
FreeMoCap's full multi-camera pipeline can be added later.
This module is the ONLY place that imports mediapipe.
"""

from __future__ import annotations

import cv2
import mediapipe as mp
import numpy as np
from scipy.ndimage import uniform_filter1d

from processing.landmark_contract import (
    LANDMARK_INDICES,
    LandmarkFrame,
    LandmarkPoint,
    LandmarkTimeSeries,
)


def extract_landmarks(video_path: str) -> LandmarkTimeSeries:
    """Extract body landmarks from video using MediaPipe Pose.

    Returns a LandmarkTimeSeries with smoothed coordinates.
    """
    pose = mp.solutions.pose.Pose(
        static_image_mode=False,
        model_complexity=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frames: list[LandmarkFrame] = []
    frame_idx = 0

    while cap.isOpened():
        ret, frame_bgr = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        lf = LandmarkFrame(frame_index=frame_idx)
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            for name, idx in LANDMARK_INDICES.items():
                lm = landmarks[idx]
                setattr(lf, name, LandmarkPoint(
                    x=lm.x, y=lm.y, z=lm.z, visibility=lm.visibility
                ))

        frames.append(lf)
        frame_idx += 1

    cap.release()
    pose.close()

    series = LandmarkTimeSeries(frames=frames, frame_rate=fps)
    _smooth_landmarks(series)
    return series


def _smooth_landmarks(series: LandmarkTimeSeries, window: int = 5) -> None:
    """Apply low-pass smoothing to landmark coordinates."""
    if len(series.frames) < window:
        return

    landmark_names = list(LANDMARK_INDICES.keys())

    for name in landmark_names:
        xs = np.array([getattr(f, name).x for f in series.frames])
        ys = np.array([getattr(f, name).y for f in series.frames])
        zs = np.array([getattr(f, name).z for f in series.frames])

        xs_smooth = uniform_filter1d(xs, size=window)
        ys_smooth = uniform_filter1d(ys, size=window)
        zs_smooth = uniform_filter1d(zs, size=window)

        for i, frame in enumerate(series.frames):
            pt = getattr(frame, name)
            pt.x = float(xs_smooth[i])
            pt.y = float(ys_smooth[i])
            pt.z = float(zs_smooth[i])
