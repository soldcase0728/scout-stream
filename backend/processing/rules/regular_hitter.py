"""Coaching rules for regular hitters (R1-R6)."""

from __future__ import annotations


def _rule_r1(metrics: dict, deltas: dict, timing: dict) -> dict | None:
    """R1: Late posture rise into contact."""
    d_lc = deltas.get("launch_to_contact", {})
    spine_delta = d_lc.get("delta_spine_angle", 0)
    spine_z_delta = d_lc.get("delta_spine_position_y", 0)  # Y is vertical in MediaPipe

    # Spine angle increases (posture opens) and body rises
    if abs(spine_delta) > 8 or abs(spine_z_delta) > 0.03:
        return {
            "rule_id": "R1",
            "name": "late_posture_rise",
            "priority": "high",
            "what_happened": "Posture rose late into contact.",
            "what_it_likely_means": "The upper body is likely taking over too early or the hitter is losing posture through delivery.",
            "likely_effect": "Weaker directional control, reduced adjustability, inconsistent contact quality.",
            "coaching_focus": "Maintain trunk angle and body posture from launch through contact.",
            "short_coaching_cue": "Stay in your posture through contact.",
        }
    return None


def _rule_r2(metrics: dict, deltas: dict, timing: dict) -> dict | None:
    """R2: Early shoulder opening."""
    launch = metrics.get("launch", {})
    shoulder_angle = abs(launch.get("shoulder_angle", 0))
    separation = launch.get("separation", 0)

    if shoulder_angle > 20 or abs(separation) < 3:
        return {
            "rule_id": "R2",
            "name": "early_shoulder_opening",
            "priority": "high",
            "what_happened": "Shoulders opened too early relative to the hips.",
            "what_it_likely_means": "The upper half is getting ahead of the lower half.",
            "likely_effect": "Rushed swing, reduced sequence, weak pull-side rollover, less adjustability.",
            "coaching_focus": "Delay shoulder rotation and improve lower-half lead.",
            "short_coaching_cue": "Let the hips win first.",
        }
    return None


def _rule_r3(metrics: dict, deltas: dict, timing: dict) -> dict | None:
    """R3: Weak lower-half sequence."""
    d_sl = deltas.get("start_to_launch", {})
    hip_delta = abs(d_sl.get("delta_hip_angle", 0))
    sep_launch = abs(metrics.get("launch", {}).get("separation", 0))

    if hip_delta < 5 and sep_launch < 4:
        return {
            "rule_id": "R3",
            "name": "weak_lower_half_sequence",
            "priority": "high",
            "what_happened": "The lower half did not create enough lead into delivery.",
            "what_it_likely_means": "The hitter may be arm-dominant or not organizing force well from the ground up.",
            "likely_effect": "Reduced power, inconsistent timing, flatter or weaker delivery.",
            "coaching_focus": "Create a more effective lower-half move before upper-body release.",
            "short_coaching_cue": "Move from the ground up.",
        }
    return None


def _rule_r4(metrics: dict, deltas: dict, timing: dict) -> dict | None:
    """R4: Excessive forward leak before launch."""
    d_sl = deltas.get("start_to_launch", {})
    forward_drift = abs(d_sl.get("delta_spine_position_x", 0))

    if forward_drift > 0.05:
        return {
            "rule_id": "R4",
            "name": "excessive_forward_leak",
            "priority": "medium",
            "what_happened": "The body drifted forward too early before launch.",
            "what_it_likely_means": "The hitter is leaking into the attack instead of gathering into it.",
            "likely_effect": "Timing instability, poor adjustability, weak balance at contact.",
            "coaching_focus": "Control forward movement during gather and arrive more organized at launch.",
            "short_coaching_cue": "Do not drift into the swing.",
        }
    return None


def _rule_r5(metrics: dict, deltas: dict, timing: dict) -> dict | None:
    """R5: Front side too open at launch."""
    launch = metrics.get("launch", {})
    foot_angle = abs(launch.get("lead_foot_angle", 0))
    hip_angle = abs(launch.get("hip_angle", 0))

    if foot_angle > 25 and hip_angle > 15:
        return {
            "rule_id": "R5",
            "name": "front_side_too_open",
            "priority": "medium",
            "what_happened": "The front side arrived too open at launch.",
            "what_it_likely_means": "The hitter may be leaking rotationally before the swing is organized.",
            "likely_effect": "Pull-off, blocked direction, early upper-body action.",
            "coaching_focus": "Improve front-side organization and foot direction into launch.",
            "short_coaching_cue": "Land more controlled and hit from it.",
        }
    return None


def _rule_r6(metrics: dict, deltas: dict, timing: dict) -> dict | None:
    """R6: Contact posture collapse."""
    d_lc = deltas.get("launch_to_contact", {})
    spine_delta = abs(d_lc.get("delta_spine_angle", 0))
    sep_delta = abs(d_lc.get("delta_separation", 0))

    if spine_delta > 10 and sep_delta > 8:
        return {
            "rule_id": "R6",
            "name": "contact_posture_collapse",
            "priority": "medium",
            "what_happened": "Contact posture collapsed late in the swing.",
            "what_it_likely_means": "The hitter is not maintaining body organization through the strike zone.",
            "likely_effect": "Poor contact consistency, weak direction, loss of barrel control.",
            "coaching_focus": "Maintain posture and organization all the way through contact.",
            "short_coaching_cue": "Hold shape through the hit.",
        }
    return None


REGULAR_RULES = [
    {"id": "R1", "applies_to": ["regular", "left_slap"], "fn": _rule_r1},
    {"id": "R2", "applies_to": ["regular", "left_slap"], "fn": _rule_r2},
    {"id": "R3", "applies_to": ["regular"], "fn": _rule_r3},
    {"id": "R4", "applies_to": ["regular"], "fn": _rule_r4},
    {"id": "R5", "applies_to": ["regular", "left_slap"], "fn": _rule_r5},
    {"id": "R6", "applies_to": ["regular"], "fn": _rule_r6},
]
