"""Tests for the metrics engine - core formula correctness."""

import numpy as np
import pytest

from processing.metrics_engine import (
    compute_all_metrics,
    _compute_spine_angle,
    _compute_rotation_angle,
    _compute_deltas,
)
from processing.landmark_contract import LandmarkTimeSeries


class TestSpineAngle:
    def test_vertical_trunk_is_near_zero(self):
        """Perfectly vertical trunk should have ~0 degree angle from vertical."""
        pelvis = np.array([0.0, 0.6, 0.0])
        shoulder = np.array([0.0, 0.4, 0.0])  # Directly above (lower Y = higher)
        angle = _compute_spine_angle(pelvis, shoulder)
        assert abs(angle) < 5  # Near vertical

    def test_leaned_trunk_has_larger_angle(self):
        """Forward-leaned trunk should show larger angle."""
        pelvis = np.array([0.0, 0.6, 0.0])
        shoulder_vertical = np.array([0.0, 0.4, 0.0])
        shoulder_leaned = np.array([0.1, 0.4, 0.0])
        angle_vertical = _compute_spine_angle(pelvis, shoulder_vertical)
        angle_leaned = _compute_spine_angle(pelvis, shoulder_leaned)
        assert angle_leaned > angle_vertical


class TestRotationAngle:
    def test_square_hips_near_zero(self):
        """Square hips (symmetric) should be near 0."""
        left = np.array([-0.1, 0.6, 0.0])
        right = np.array([0.1, 0.6, 0.0])
        angle = _compute_rotation_angle(left, right)
        assert abs(angle) < 5

    def test_rotated_hips_show_angle(self):
        """Hips rotated in XZ plane should show non-zero angle."""
        left = np.array([-0.1, 0.6, -0.05])
        right = np.array([0.1, 0.6, 0.05])
        angle = _compute_rotation_angle(left, right)
        assert abs(angle) > 5


class TestSeparation:
    def test_separation_is_difference(self):
        """Separation = shoulder angle - hip angle."""
        assert _compute_separation(30.0, 20.0) == 10.0
        assert _compute_separation(20.0, 30.0) == -10.0
        assert _compute_separation(15.0, 15.0) == 0.0


class TestDeltas:
    def test_delta_computation(self):
        """Deltas should be difference between two checkpoints."""
        a = {"spine_angle": 18.0, "hip_angle": 5.0, "separation": -3.0}
        b = {"spine_angle": 25.0, "hip_angle": 15.0, "separation": 4.0}
        d = _compute_deltas(a, b)
        assert d["delta_spine_angle"] == 7.0
        assert d["delta_hip_angle"] == 10.0
        assert d["delta_separation"] == 7.0


class TestComputeAllMetrics:
    def test_produces_all_keys(self, swing_series: LandmarkTimeSeries):
        result = compute_all_metrics(swing_series, 5, 30, 50)
        assert "metrics" in result
        assert "deltas" in result
        assert "timing" in result
        assert set(result["metrics"].keys()) == {"start", "launch", "contact"}
        assert "start_to_launch" in result["deltas"]
        assert result["timing"]["frames_start_to_launch"] == 25
        assert result["timing"]["frames_launch_to_contact"] == 20

    def test_each_checkpoint_has_all_metrics(self, swing_series: LandmarkTimeSeries):
        result = compute_all_metrics(swing_series, 5, 30, 50)
        expected_keys = {
            "spine_angle", "spine_angle_side", "spine_position_x",
            "spine_position_y", "spine_position_z", "lead_foot_angle",
            "rear_foot_angle", "hip_angle", "shoulder_angle",
            "shoulder_tilt", "separation",
        }
        for checkpoint in ["start", "launch", "contact"]:
            assert set(result["metrics"][checkpoint].keys()) == expected_keys

    def test_metrics_are_finite(self, swing_series: LandmarkTimeSeries):
        result = compute_all_metrics(swing_series, 5, 30, 50)
        for checkpoint in ["start", "launch", "contact"]:
            for key, val in result["metrics"][checkpoint].items():
                assert np.isfinite(val), f"{checkpoint}.{key} is not finite: {val}"


def _compute_separation(shoulder: float, hip: float) -> float:
    return shoulder - hip
