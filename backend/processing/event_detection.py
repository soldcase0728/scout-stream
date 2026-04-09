"""Event detection engine.

Detects three public events for each swing:
  - Start: last quiet frame before coordinated movement begins
  - Launch: first committed attack frame (after full-foot plant)
  - Contact: estimated impact frame

Internally also detects Plant (full-foot stable plant) to assist event logic.
Plant means full foot down, heel included, stable enough to accept force.

Key design: Contact is detected first (peak delivery), then Launch is found
by working backward from Contact to find when the committed attack began.
This prevents triggering Launch too early on gather/stride movement.
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

    # Detect in this order: Start, Contact, Plant, Launch
    # Contact first so Launch can anchor backward from it
    start = _detect_start(features, swing_type)
    contact = _detect_contact_global(features, swing_type)
    plant = _detect_plant(features, swing_type, start, contact)
    launch = _detect_launch(features, swing_type, start, plant, contact)

    # Enforce ordering
    if launch <= start:
        launch = start + 1
    if launch >= contact:
        launch = contact - 1
    if contact <= start:
        contact = n - 1
        launch = max(start + 1, contact - 5)

    launch = max(0, min(launch, n - 1))
    contact = max(0, min(contact, n - 1))

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
    foot_horiz_speed = np.linalg.norm(np.diff(lead_foot_pos[:, [0, 2]], axis=0), axis=1)
    pelvis_angular_vel = np.abs(np.diff(pelvis_angle))
    shoulder_angular_vel = np.abs(np.diff(shoulder_angle))

    # Pad to match frame count
    pelvis_speed = np.append(pelvis_speed, 0)
    shoulder_speed = np.append(shoulder_speed, 0)
    wrist_speed = np.append(wrist_speed, 0)
    foot_vert_vel = np.append(foot_vert_vel, 0)
    foot_horiz_speed = np.append(foot_horiz_speed, 0)
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
        "foot_horiz_speed": foot_horiz_speed,
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


def _detect_contact_global(features: dict, swing_type: str) -> int:
    """Estimated impact frame - peak wrist speed in the swing.

    Detected before Launch so Launch can anchor backward from it.
    """
    wrist_s = features["wrist_speed"]
    n = len(wrist_s)

    # Find peak wrist speed in the second half of the clip
    # (contact should be in the later portion)
    search_start = n // 3
    search_region = wrist_s[search_start:]
    if len(search_region) == 0:
        return n - 1

    peak_offset = int(np.argmax(search_region))
    return search_start + peak_offset


def _detect_plant(features: dict, swing_type: str, start: int, contact: int) -> int | None:
    """Detect full-foot stable plant (heel down, stable).

    Plant is only valid when foot is fully down including heel,
    stable enough to accept force. Toe touch does not count.

    Search between start and contact for the frame where the lead foot
    horizontal and vertical movement both settle.
    """
    foot_vert = features["foot_vert_vel"]
    foot_horiz = features["foot_horiz_speed"]
    n = len(foot_vert)

    search_start = start + 3
    search_end = contact - 1
    if search_start >= search_end or search_start >= n - 5:
        return None

    # Look for frame where both vertical and horizontal foot movement settle
    vert_threshold = np.std(foot_vert[search_start:search_end]) * 0.4
    horiz_threshold = np.std(foot_horiz[search_start:search_end]) * 0.4

    # Search backward from contact to find where foot became stable
    for i in range(search_end - 1, search_start, -1):
        window_vert = np.abs(foot_vert[max(search_start, i - 2) : i + 1])
        window_horiz = foot_horiz[max(search_start, i - 2) : i + 1]
        if np.any(window_vert > vert_threshold) or np.any(window_horiz > horiz_threshold):
            # This frame has movement - plant is the next stable frame after this
            plant = min(i + 1, search_end)
            return plant

    return search_start


def _detect_launch(
    features: dict, swing_type: str, start: int, plant: int | None, contact: int
) -> int:
    """First committed attack frame - transition from gather to delivery.

    Strategy: work BACKWARD from contact to find when the explosive
    acceleration began. Launch is when the body transitions from
    gather/movement into committed delivery.
    """
    pelvis_av = features["pelvis_angular_vel"]
    wrist_s = features["wrist_speed"]
    shoulder_av = features["shoulder_angular_vel"]
    n = len(pelvis_av)

    # Combined delivery signal (normalized)
    delivery_signal = (
        pelvis_av / (pelvis_av.max() + 1e-8) +
        wrist_s / (wrist_s.max() + 1e-8) +
        shoulder_av / (shoulder_av.max() + 1e-8)
    )

    # Walk backward from contact to find where delivery signal drops
    # below threshold - that's where the attack acceleration began
    search_start = max(start + 1, 0)
    peak_signal = delivery_signal[max(0, contact - 3) : contact + 1].max()

    # Use 50% of peak as threshold (higher = finds launch earlier/further from contact)
    launch_threshold = peak_signal * 0.50

    launch = contact - 1
    for i in range(contact - 1, search_start, -1):
        if delivery_signal[i] < launch_threshold:
            launch = i + 1
            break

    # Enforce minimum gap: launch must be at least 5% of total swing
    # duration before contact (prevents launch = contact - 1)
    total_duration = contact - start
    min_gap = max(3, int(total_duration * 0.08))
    if contact - launch < min_gap:
        launch = contact - min_gap

    # If plant is detected and is a reasonable launch candidate, use it
    if plant is not None and start < plant < contact:
        # Plant is a strong anchor for launch - use it if it's
        # in a reasonable range (within the last 40% of the swing)
        swing_progress = (plant - start) / max(total_duration, 1)
        if swing_progress > 0.4:
            # Plant is late enough to be a good launch anchor
            launch = plant

    # Final bounds check
    if launch >= contact:
        launch = contact - min_gap
    if launch <= start:
        launch = start + 1

    return max(search_start, min(launch, contact - 2))


def _score_confidence(features: dict, start: int, launch: int, contact: int) -> float:
    """Score event detection confidence 0-1."""
    score = 0.5

    # Better if there's clear velocity difference between start and contact region
    start_region = features["pelvis_speed"][max(0, start - 2) : start + 2]
    launch_region = features["pelvis_speed"][max(0, launch - 2) : launch + 2]
    if len(start_region) > 0 and len(launch_region) > 0:
        if launch_region.mean() > start_region.mean() * 1.5:
            score += 0.15

    # Better if launch-to-contact timing is reasonable (2-30 frames)
    frames_launch_to_contact = contact - launch
    if 2 <= frames_launch_to_contact <= 30:
        score += 0.15

    # Better if we have clear wrist speed peak
    wrist_peak = features["wrist_speed"][contact]
    wrist_mean = features["wrist_speed"].mean()
    if wrist_peak > wrist_mean * 2:
        score += 0.1

    # Better if start-to-launch is reasonable portion of total
    total = contact - start
    if total > 0:
        launch_ratio = (launch - start) / total
        if 0.5 < launch_ratio < 0.98:
            score += 0.1

    return min(score, 1.0)
