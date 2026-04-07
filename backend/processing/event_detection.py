"""Event detection engine.

Detects three public events for each swing:
  - Start: last quiet frame before coordinated movement begins
  - Launch: first committed attack frame
  - Contact: estimated impact frame

Internally also detects Plant (full-foot stable plant) to assist event logic.
Plant means full foot down, heel included, stable enough to accept force.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from processing.landmark_contract import LandmarkTimeSeries


@dataclass
class DetectedEvents:
    start_frame: int
    launch_frame: int
    contact_frame: int
    plant_frame: int | None = None
    confidence: float = 0.0


def detect_events(series: LandmarkTimeSeries, swing_type: str = "regular") -> DetectedEvents:
    """Detect Start, Launch, Contact from landmark time series."""
    features = _compute_features(series)
    n = len(features["pelvis_speed"])

    if n < 10:
        return DetectedEvents(
            start_frame=0, launch_frame=n // 2, contact_frame=n - 1, confidence=0.1
        )

    start = _detect_start(features, swing_type)
    plant = _detect_plant(features, swing_type, start)
    launch = _detect_launch(features, swing_type, start, plant)
    contact = _detect_contact(features, swing_type, launch)

    # Enforce ordering
    if launch <= start:
        launch = start + max(1, (contact - start) // 2) if contact > start else start + 1
    if contact <= launch:
        contact = min(launch + 5, n - 1)

    confidence = _score_confidence(features, start, launch, contact)

    return DetectedEvents(
        start_frame=start,
        launch_frame=launch,
        contact_frame=contact,
        plant_frame=plant,
        confidence=confidence,
    )


def _compute_features(series: LandmarkTimeSeries) -> dict[str, np.ndarray]:
    """Compute frame-level movement features from landmarks."""
    n = series.num_frames
    pelvis_pos = np.zeros((n, 3))
    shoulder_pos = np.zeros((n, 3))
    lead_foot_pos = np.zeros((n, 3))
    wrist_pos = np.zeros((n, 3))
    pelvis_angle = np.zeros(n)
    shoulder_angle = np.zeros(n)

    for i, f in enumerate(series.frames):
        pelvis_pos[i] = f.pelvis_midpoint()
        shoulder_pos[i] = f.shoulder_midpoint()

        # Use left foot as lead for right-handed, right foot for left-handed
        lead_foot_pos[i] = f.point_as_array("left_heel")
        wrist_pos[i] = (f.point_as_array("left_wrist") + f.point_as_array("right_wrist")) / 2

        # Pelvis rotation angle (XY plane)
        hip_vec = f.point_as_array("right_hip") - f.point_as_array("left_hip")
        pelvis_angle[i] = np.degrees(np.arctan2(hip_vec[1], hip_vec[0]))

        # Shoulder rotation angle (XY plane)
        sh_vec = f.point_as_array("right_shoulder") - f.point_as_array("left_shoulder")
        shoulder_angle[i] = np.degrees(np.arctan2(sh_vec[1], sh_vec[0]))

    # Velocities (frame-to-frame displacement)
    pelvis_speed = np.linalg.norm(np.diff(pelvis_pos, axis=0), axis=1)
    shoulder_speed = np.linalg.norm(np.diff(shoulder_pos, axis=0), axis=1)
    wrist_speed = np.linalg.norm(np.diff(wrist_pos, axis=0), axis=1)
    foot_vert_vel = np.diff(lead_foot_pos[:, 1])  # vertical movement
    pelvis_angular_vel = np.abs(np.diff(pelvis_angle))
    shoulder_angular_vel = np.abs(np.diff(shoulder_angle))

    # Pad to match frame count
    pelvis_speed = np.append(pelvis_speed, 0)
    shoulder_speed = np.append(shoulder_speed, 0)
    wrist_speed = np.append(wrist_speed, 0)
    foot_vert_vel = np.append(foot_vert_vel, 0)
    pelvis_angular_vel = np.append(pelvis_angular_vel, 0)
    shoulder_angular_vel = np.append(shoulder_angular_vel, 0)

    return {
        "pelvis_pos": pelvis_pos,
        "shoulder_pos": shoulder_pos,
        "lead_foot_pos": lead_foot_pos,
        "wrist_pos": wrist_pos,
        "pelvis_speed": pelvis_speed,
        "shoulder_speed": shoulder_speed,
        "wrist_speed": wrist_speed,
        "foot_vert_vel": foot_vert_vel,
        "pelvis_angle": pelvis_angle,
        "shoulder_angle": shoulder_angle,
        "pelvis_angular_vel": pelvis_angular_vel,
        "shoulder_angular_vel": shoulder_angular_vel,
    }


def _detect_start(features: dict, swing_type: str) -> int:
    """Last stable frame before coordinated movement begins."""
    combined = features["pelvis_speed"] + features["shoulder_speed"]
    threshold = np.median(combined) + np.std(combined) * 0.5

    n = len(combined)
    # Walk backward from peak to find last quiet frame
    peak = int(np.argmax(combined))
    search_end = max(peak // 2, 5)

    for i in range(search_end, 0, -1):
        window = combined[max(0, i - 3) : i + 1]
        if np.all(window < threshold):
            return i
    return 0


def _detect_plant(features: dict, swing_type: str, start: int) -> int | None:
    """Detect full-foot stable plant (heel down, stable).

    For slappers: plant is only valid when foot is fully down including heel,
    stable enough to accept force. Toe touch does not count.
    """
    foot_vert = features["foot_vert_vel"]
    n = len(foot_vert)

    # Look for the frame where lead foot vertical movement settles
    search_start = start + 3
    if search_start >= n - 5:
        return None

    foot_pos = features["lead_foot_pos"][:, 1]  # vertical
    threshold = np.std(foot_vert[search_start:]) * 0.3

    for i in range(search_start, n - 4):
        window = np.abs(foot_vert[i : i + 3])
        if np.all(window < threshold):
            return i

    return None


def _detect_launch(features: dict, swing_type: str, start: int, plant: int | None) -> int:
    """First committed attack frame - transition from gather to go."""
    search_from = plant - 2 if plant and plant > start else start + 3
    search_from = max(search_from, start + 1)

    pelvis_av = features["pelvis_angular_vel"]
    wrist_s = features["wrist_speed"]
    n = len(pelvis_av)

    # Launch = first frame after search_from where pelvis angular velocity
    # and wrist speed both begin sustained increase
    pav_threshold = np.median(pelvis_av) + np.std(pelvis_av) * 0.8
    ws_threshold = np.median(wrist_s) + np.std(wrist_s) * 0.5

    for i in range(search_from, n - 3):
        if pelvis_av[i] > pav_threshold or wrist_s[i] > ws_threshold:
            # Check it's sustained for 2+ frames
            if i + 2 < n and (pelvis_av[i + 1] > pav_threshold * 0.7 or wrist_s[i + 1] > ws_threshold * 0.7):
                return i

    # Fallback: midpoint between start and peak wrist speed
    peak_wrist = int(np.argmax(wrist_s))
    return (start + peak_wrist) // 2


def _detect_contact(features: dict, swing_type: str, launch: int) -> int:
    """Estimated impact frame - peak wrist speed after launch."""
    wrist_s = features["wrist_speed"]
    n = len(wrist_s)

    search_region = wrist_s[launch:]
    if len(search_region) == 0:
        return min(launch + 5, n - 1)

    peak_offset = int(np.argmax(search_region))
    return launch + peak_offset


def _score_confidence(features: dict, start: int, launch: int, contact: int) -> float:
    """Score event detection confidence 0-1."""
    score = 0.5

    # Better if there's clear velocity difference between start and contact region
    pelvis_at_start = features["pelvis_speed"][max(0, start - 2) : start + 2].mean()
    pelvis_at_launch = features["pelvis_speed"][max(0, launch - 2) : launch + 2].mean()
    if pelvis_at_launch > pelvis_at_start * 2:
        score += 0.2

    # Better if launch < contact and reasonable timing
    frames_launch_to_contact = contact - launch
    if 5 <= frames_launch_to_contact <= 30:
        score += 0.15

    # Better if we have clear wrist speed peak
    wrist_peak = features["wrist_speed"][contact]
    wrist_mean = features["wrist_speed"].mean()
    if wrist_peak > wrist_mean * 2:
        score += 0.15

    return min(score, 1.0)
