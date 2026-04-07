"""Tests for the interpretation engine and coaching rules."""

import pytest

from processing.interpretation_engine import interpret_swing


class TestInterpretationEngine:
    def test_output_structure(self):
        """Interpretation should always return required keys."""
        metrics = {
            "start": {"spine_angle": 18, "hip_angle": 5, "shoulder_angle": 8, "separation": 3,
                       "spine_position_x": 0, "spine_position_y": 0.6, "spine_position_z": 0,
                       "lead_foot_angle": 5, "rear_foot_angle": -10, "shoulder_tilt": 2,
                       "spine_angle_side": 1},
            "launch": {"spine_angle": 19, "hip_angle": 12, "shoulder_angle": 6, "separation": -6,
                        "spine_position_x": 0.02, "spine_position_y": 0.59, "spine_position_z": 0,
                        "lead_foot_angle": 15, "rear_foot_angle": -5, "shoulder_tilt": 4,
                        "spine_angle_side": 2},
            "contact": {"spine_angle": 27, "hip_angle": 34, "shoulder_angle": 40, "separation": 6,
                         "spine_position_x": 0.05, "spine_position_y": 0.57, "spine_position_z": 0,
                         "lead_foot_angle": 22, "rear_foot_angle": 5, "shoulder_tilt": 8,
                         "spine_angle_side": 5},
        }
        deltas = {
            "start_to_launch": {"delta_spine_angle": 1, "delta_hip_angle": 7,
                                 "delta_shoulder_angle": -2, "delta_separation": -9,
                                 "delta_spine_position_x": 0.02, "delta_spine_position_y": -0.01,
                                 "delta_spine_position_z": 0},
            "launch_to_contact": {"delta_spine_angle": 8, "delta_hip_angle": 22,
                                   "delta_shoulder_angle": 34, "delta_separation": 12,
                                   "delta_spine_position_x": 0.03, "delta_spine_position_y": -0.02,
                                   "delta_spine_position_z": 0},
            "start_to_contact": {"delta_spine_angle": 9, "delta_hip_angle": 29,
                                  "delta_shoulder_angle": 32, "delta_separation": 3,
                                  "delta_spine_position_x": 0.05, "delta_spine_position_y": -0.03,
                                  "delta_spine_position_z": 0},
        }
        timing = {"frames_start_to_launch": 25, "frames_launch_to_contact": 15,
                   "frames_start_to_contact": 40}

        result = interpret_swing(metrics, deltas, timing, "regular")
        assert "what_happened" in result
        assert "what_it_means" in result
        assert "what_to_coach_next" in result
        assert "rules_triggered" in result
        assert "severity" in result

    def test_posture_rise_triggers_r1(self):
        """R1 should trigger when spine angle changes too much launch to contact."""
        metrics = {
            "start": {"spine_angle": 18, "hip_angle": 5, "shoulder_angle": 8, "separation": 3,
                       "spine_position_x": 0, "spine_position_y": 0.6, "spine_position_z": 0,
                       "lead_foot_angle": 5, "rear_foot_angle": -10, "shoulder_tilt": 2,
                       "spine_angle_side": 1},
            "launch": {"spine_angle": 19, "hip_angle": 12, "shoulder_angle": 6, "separation": -6,
                        "spine_position_x": 0.01, "spine_position_y": 0.59, "spine_position_z": 0,
                        "lead_foot_angle": 15, "rear_foot_angle": -5, "shoulder_tilt": 4,
                        "spine_angle_side": 2},
            "contact": {"spine_angle": 30, "hip_angle": 34, "shoulder_angle": 40, "separation": 6,
                         "spine_position_x": 0.04, "spine_position_y": 0.55, "spine_position_z": 0,
                         "lead_foot_angle": 22, "rear_foot_angle": 5, "shoulder_tilt": 8,
                         "spine_angle_side": 5},
        }
        deltas = {
            "start_to_launch": {"delta_spine_angle": 1, "delta_hip_angle": 7,
                                 "delta_spine_position_y": -0.01},
            "launch_to_contact": {"delta_spine_angle": 11, "delta_hip_angle": 22,
                                   "delta_spine_position_y": -0.04,
                                   "delta_separation": 12},
            "start_to_contact": {"delta_spine_angle": 12, "delta_hip_angle": 29,
                                  "delta_spine_position_y": -0.05},
        }
        timing = {"frames_start_to_launch": 25, "frames_launch_to_contact": 15,
                   "frames_start_to_contact": 40}

        result = interpret_swing(metrics, deltas, timing, "regular")
        rule_ids = [r["rule_id"] for r in result["rules_triggered"]]
        assert "R1" in rule_ids

    def test_no_issue_returns_c2(self):
        """When no significant issues, C2 should be the only rule."""
        metrics = {
            "start": {"spine_angle": 18, "hip_angle": 5, "shoulder_angle": 8, "separation": 3,
                       "spine_position_x": 0, "spine_position_y": 0.6, "spine_position_z": 0,
                       "lead_foot_angle": 5, "rear_foot_angle": -10, "shoulder_tilt": 2,
                       "spine_angle_side": 1},
            "launch": {"spine_angle": 19, "hip_angle": 15, "shoulder_angle": 8, "separation": -7,
                        "spine_position_x": 0.01, "spine_position_y": 0.59, "spine_position_z": 0,
                        "lead_foot_angle": 10, "rear_foot_angle": -5, "shoulder_tilt": 3,
                        "spine_angle_side": 1.5},
            "contact": {"spine_angle": 21, "hip_angle": 30, "shoulder_angle": 35, "separation": 5,
                         "spine_position_x": 0.02, "spine_position_y": 0.58, "spine_position_z": 0,
                         "lead_foot_angle": 18, "rear_foot_angle": 3, "shoulder_tilt": 5,
                         "spine_angle_side": 2},
        }
        deltas = {
            "start_to_launch": {"delta_spine_angle": 1, "delta_hip_angle": 10,
                                 "delta_spine_position_x": 0.01,
                                 "delta_spine_position_y": -0.01,
                                 "delta_spine_position_z": 0,
                                 "delta_separation": -10},
            "launch_to_contact": {"delta_spine_angle": 2, "delta_hip_angle": 15,
                                   "delta_spine_position_y": -0.01,
                                   "delta_separation": 12},
            "start_to_contact": {"delta_spine_angle": 3, "delta_hip_angle": 25,
                                  "delta_spine_position_y": -0.02},
        }
        timing = {"frames_start_to_launch": 28, "frames_launch_to_contact": 14,
                   "frames_start_to_contact": 42}

        result = interpret_swing(metrics, deltas, timing, "regular")
        assert result["severity"] == "low"

    def test_slap_rules_apply_for_slap_type(self):
        """Slap-specific rules should trigger for left_slap swing type."""
        metrics = {
            "start": {"spine_angle": 18, "hip_angle": 5, "shoulder_angle": 8, "separation": 3,
                       "spine_position_x": 0, "spine_position_y": 0.6, "spine_position_z": 0,
                       "lead_foot_angle": 5, "rear_foot_angle": -10, "shoulder_tilt": 2,
                       "spine_angle_side": 1},
            "launch": {"spine_angle": 20, "hip_angle": 8, "shoulder_angle": 22, "separation": 14,
                        "spine_position_x": 0.08, "spine_position_y": 0.55, "spine_position_z": 0,
                        "lead_foot_angle": 25, "rear_foot_angle": -3, "shoulder_tilt": 5,
                        "spine_angle_side": 3},
            "contact": {"spine_angle": 25, "hip_angle": 28, "shoulder_angle": 38, "separation": 10,
                         "spine_position_x": 0.12, "spine_position_y": 0.52, "spine_position_z": 0,
                         "lead_foot_angle": 28, "rear_foot_angle": 4, "shoulder_tilt": 7,
                         "spine_angle_side": 4},
        }
        deltas = {
            "start_to_launch": {"delta_spine_position_x": 0.08,
                                 "delta_spine_position_y": -0.05,
                                 "delta_spine_position_z": 0,
                                 "delta_hip_angle": 3, "delta_spine_angle": 2},
            "launch_to_contact": {"delta_spine_angle": 5,
                                   "delta_spine_position_y": -0.03,
                                   "delta_separation": -4},
            "start_to_contact": {"delta_spine_position_y": -0.08},
        }
        timing = {"frames_start_to_launch": 30, "frames_launch_to_contact": 12,
                   "frames_start_to_contact": 42}

        result = interpret_swing(metrics, deltas, timing, "left_slap")
        rule_ids = [r["rule_id"] for r in result["rules_triggered"]]
        # Should have at least one slap-specific rule
        slap_rules = [r for r in rule_ids if r.startswith("S")]
        assert len(slap_rules) > 0
