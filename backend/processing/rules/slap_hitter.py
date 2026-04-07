"""Coaching rules for left-handed slap hitters (S1-S5)."""

from __future__ import annotations


def _rule_s1(metrics: dict, deltas: dict, timing: dict) -> dict | None:
    """S1: Rising through movement into contact."""
    d_sl = deltas.get("start_to_launch", {})
    d_lc = deltas.get("launch_to_contact", {})
    rise_sl = abs(d_sl.get("delta_spine_position_y", 0))
    rise_lc = abs(d_lc.get("delta_spine_position_y", 0))

    if rise_sl > 0.02 and rise_lc > 0.01:
        return {
            "rule_id": "S1",
            "name": "rising_through_movement",
            "priority": "high",
            "what_happened": "The body rose during the move and continued rising into contact.",
            "what_it_likely_means": "The slapper is floating instead of staying athletic and grounded.",
            "likely_effect": "Inconsistent barrel control, weak directional pressure, timing problems.",
            "coaching_focus": "Stay lower and more controlled through movement and delivery.",
            "short_coaching_cue": "Move low and stay low.",
        }
    return None


def _rule_s2(metrics: dict, deltas: dict, timing: dict) -> dict | None:
    """S2: Early upper-body takeover."""
    launch = metrics.get("launch", {})
    shoulder_angle = abs(launch.get("shoulder_angle", 0))
    separation = abs(launch.get("separation", 0))

    if shoulder_angle > 18 and separation < 4:
        return {
            "rule_id": "S2",
            "name": "early_upper_body_takeover",
            "priority": "high",
            "what_happened": "The upper body got involved too early in the delivery.",
            "what_it_likely_means": "The slapper is moving and swinging as one unit instead of transitioning cleanly into delivery.",
            "likely_effect": "Weak hard slap, poor adjustability, rushed contact.",
            "coaching_focus": "Keep the upper body quieter into launch and deliver later.",
            "short_coaching_cue": "Stay organized, then deliver.",
        }
    return None


def _rule_s3(metrics: dict, deltas: dict, timing: dict) -> dict | None:
    """S3: Over-open front side at launch."""
    launch = metrics.get("launch", {})
    foot_angle = abs(launch.get("lead_foot_angle", 0))
    hip_angle = abs(launch.get("hip_angle", 0))

    if foot_angle > 22 and hip_angle > 14:
        return {
            "rule_id": "S3",
            "name": "over_open_front_side_slap",
            "priority": "high",
            "what_happened": "The front side got too open too early.",
            "what_it_likely_means": "Direction is leaking before the hitter gets through contact.",
            "likely_effect": "Pull-off, weak left-side pressure, inconsistent hard-slap direction.",
            "coaching_focus": "Improve foot direction and front-side control into launch.",
            "short_coaching_cue": "Do not show open too early.",
        }
    return None


def _rule_s4(metrics: dict, deltas: dict, timing: dict) -> dict | None:
    """S4: Weak delivery organization at launch."""
    launch = metrics.get("launch", {})
    separation = abs(launch.get("separation", 0))
    d_sl = deltas.get("start_to_launch", {})
    hip_delta = abs(d_sl.get("delta_hip_angle", 0))

    if separation < 3 and hip_delta < 4:
        return {
            "rule_id": "S4",
            "name": "weak_delivery_organization",
            "priority": "high",
            "what_happened": "The body did not organize cleanly into the delivery phase.",
            "what_it_likely_means": "The athlete is reaching contact without a stable transition from movement to swing.",
            "likely_effect": "Late contact, weak barrel control, limited ability to vary soft slap versus hard slap.",
            "coaching_focus": "Create a cleaner organized launch position before contact.",
            "short_coaching_cue": "Arrive organized, then attack.",
        }
    return None


def _rule_s5(metrics: dict, deltas: dict, timing: dict) -> dict | None:
    """S5: Excessive drift through launch."""
    d_sl = deltas.get("start_to_launch", {})
    forward_drift = abs(d_sl.get("delta_spine_position_x", 0))
    lateral_drift = abs(d_sl.get("delta_spine_position_z", 0))

    if forward_drift > 0.06 or lateral_drift > 0.04:
        return {
            "rule_id": "S5",
            "name": "excessive_drift_slap",
            "priority": "medium",
            "what_happened": "The body drifted too much through launch.",
            "what_it_likely_means": "The slapper is still traveling instead of delivering.",
            "likely_effect": "Unstable contact, late barrel delivery, poor directional control.",
            "coaching_focus": "Control movement better before delivery begins.",
            "short_coaching_cue": "Travel less by launch.",
        }
    return None


SLAP_RULES = [
    {"id": "S1", "applies_to": ["left_slap"], "fn": _rule_s1},
    {"id": "S2", "applies_to": ["left_slap"], "fn": _rule_s2},
    {"id": "S3", "applies_to": ["left_slap"], "fn": _rule_s3},
    {"id": "S4", "applies_to": ["left_slap"], "fn": _rule_s4},
    {"id": "S5", "applies_to": ["left_slap"], "fn": _rule_s5},
]
