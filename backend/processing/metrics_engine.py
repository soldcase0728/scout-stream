"""Metrics engine.

Computes checkpoint metrics at Start, Launch, Contact:
  - spine angle (forward, side)
  - spine position (x, y, z)
  - lead foot angle, rear foot angle
  - hip angle (pelvis rotation)
  - shoulder angle
  - shoulder tilt
  - separation (shoulder angle - hip angle)

Also computes delta metrics between checkpoints and timing metrics.
"""

from __future__ import annotations

import numpy as np

from processing.landmark_contract import LandmarkFrame, LandmarkTimeSeries


def compute_all_metrics(
    series: LandmarkTimeSeries,
    start_frame: int,
    launch_frame: int,
    contact_frame: int,
    handedness: str = "right",
) -> dict:
    """Compute full metric set for a swing.

    Returns dict with keys: metrics, deltas, timing.
    """
    frames = series.frames
    start = frames[start_frame]
    launch = frames[launch_frame]
    contact = frames[contact_frame]

    # Determine lead/rear side based on handedness
    # Right-handed: left foot is lead; Left-handed: right foot is lead
    lead_side = "left" if handedness == "right" else "right"
    rear_side = "right" if handedness == "right" else "left"

    start_m = _checkpoint_metrics(start, lead_side, rear_side)
    launch_m = _checkpoint_metrics(launch, lead_side, rear_side)
    contact_m = _checkpoint_metrics(contact, lead_side, rear_side)

    metrics = {
        "start": start_m,
        "launch": launch_m,
        "contact": contact_m,
    }

    deltas = {
        "start_to_launch": _compute_deltas(start_m, launch_m),
        "launch_to_contact": _compute_deltas(launch_m, contact_m),
        "start_to_contact": _compute_deltas(start_m, contact_m),
    }

    timing = {
        "frames_start_to_launch": launch_frame - start_frame,
        "frames_launch_to_contact": contact_frame - launch_frame,
        "frames_start_to_contact": contact_frame - start_frame,
    }

    return {"metrics": metrics, "deltas": deltas, "timing": timing}


def _checkpoint_metrics(frame: LandmarkFrame, lead_side: str, rear_side: str) -> dict:
    """Compute all metrics at a single checkpoint frame."""
    pelvis_mid = frame.pelvis_midpoint()
    shoulder_mid = frame.shoulder_midpoint()

    spine_angle = _compute_spine_angle(pelvis_mid, shoulder_mid)
    spine_angle_side = _compute_spine_angle_side(pelvis_mid, shoulder_mid)

    hip_angle = _compute_rotation_angle(
        frame.point_as_array("left_hip"),
        frame.point_as_array("right_hip"),
    )
    shoulder_angle = _compute_rotation_angle(
        frame.point_as_array("left_shoulder"),
        frame.point_as_array("right_shoulder"),
    )
    shoulder_tilt = _compute_shoulder_tilt(
        frame.point_as_array("left_shoulder"),
        frame.point_as_array("right_shoulder"),
    )

    lead_foot_angle = _compute_foot_angle(
        frame.point_as_array(f"{lead_side}_heel"),
        frame.point_as_array(f"{lead_side}_foot_index"),
    )
    rear_foot_angle = _compute_foot_angle(
        frame.point_as_array(f"{rear_side}_heel"),
        frame.point_as_array(f"{rear_side}_foot_index"),
    )

    return {
        "spine_angle": round(spine_angle, 1),
        "spine_angle_side": round(spine_angle_side, 1),
        "spine_position_x": round(float(pelvis_mid[0]), 4),
        "spine_position_y": round(float(pelvis_mid[1]), 4),
        "spine_position_z": round(float(pelvis_mid[2]), 4),
        "lead_foot_angle": round(lead_foot_angle, 1),
        "rear_foot_angle": round(rear_foot_angle, 1),
        "hip_angle": round(hip_angle, 1),
        "shoulder_angle": round(shoulder_angle, 1),
        "shoulder_tilt": round(shoulder_tilt, 1),
        "separation": round(shoulder_angle - hip_angle, 1),
    }


def _compute_spine_angle(pelvis_mid: np.ndarray, shoulder_mid: np.ndarray) -> float:
    """Angle of trunk segment relative to vertical (forward lean in sagittal plane)."""
    trunk_vec = shoulder_mid - pelvis_mid
    # Vertical axis: in MediaPipe, Y is vertical (pointing down)
    # We measure angle from vertical
    vertical = np.array([0, -1, 0])
    cos_angle = np.dot(trunk_vec, vertical) / (np.linalg.norm(trunk_vec) + 1e-8)
    cos_angle = np.clip(cos_angle, -1, 1)
    return float(np.degrees(np.arccos(cos_angle)))


def _compute_spine_angle_side(pelvis_mid: np.ndarray, shoulder_mid: np.ndarray) -> float:
    """Trunk side bend in frontal plane."""
    trunk_vec = shoulder_mid - pelvis_mid
    # Side bend: angle of trunk vector projected onto frontal plane
    frontal_component = np.array([trunk_vec[0], 0, trunk_vec[2]])
    if np.linalg.norm(frontal_component) < 1e-8:
        return 0.0
    vertical = np.array([0, -1, 0])
    lateral_offset = trunk_vec[0]  # X component indicates side lean
    return float(np.degrees(np.arctan2(lateral_offset, abs(trunk_vec[1]) + 1e-8)))


def _compute_rotation_angle(left_point: np.ndarray, right_point: np.ndarray) -> float:
    """Rotation angle of a body line in the horizontal plane (XZ).

    0 = square to target line, positive = open, negative = closed.
    """
    vec = right_point - left_point
    return float(np.degrees(np.arctan2(vec[2], vec[0])))


def _compute_shoulder_tilt(left_sh: np.ndarray, right_sh: np.ndarray) -> float:
    """Vertical tilt of shoulder line (positive = right higher)."""
    diff_y = right_sh[1] - left_sh[1]
    diff_x = np.linalg.norm(right_sh[[0, 2]] - left_sh[[0, 2]]) + 1e-8
    return float(np.degrees(np.arctan2(diff_y, diff_x)))


def _compute_foot_angle(heel: np.ndarray, toe: np.ndarray) -> float:
    """Foot direction angle relative to forward (X axis)."""
    foot_vec = toe - heel
    return float(np.degrees(np.arctan2(foot_vec[2], foot_vec[0])))


def _compute_deltas(metrics_a: dict, metrics_b: dict) -> dict:
    """Compute change between two checkpoint metric dicts."""
    delta = {}
    for key in metrics_a:
        val_a = metrics_a[key]
        val_b = metrics_b[key]
        if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
            delta[f"delta_{key}"] = round(val_b - val_a, 2)
    return delta
