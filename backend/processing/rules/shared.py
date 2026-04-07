"""Shared coaching rules for all swing types (C1-C2)."""

from __future__ import annotations


def _rule_c1(metrics: dict, deltas: dict, timing: dict) -> dict | None:
    """C1: Timing compressed from launch to contact."""
    frames_lc = timing.get("frames_launch_to_contact", 999)

    if frames_lc < 6:
        return {
            "rule_id": "C1",
            "name": "timing_compressed",
            "priority": "medium",
            "what_happened": "The attack window from launch to contact was compressed.",
            "what_it_likely_means": "The hitter is rushing delivery or starting too late.",
            "likely_effect": "Poor adjustability, rushed barrel path, inconsistent timing.",
            "coaching_focus": "Create more organized, usable time in the attack phase.",
            "short_coaching_cue": "Give yourself more room to deliver.",
        }
    return None


def _rule_c2(metrics: dict, deltas: dict, timing: dict) -> dict | None:
    """C2: No major issue detected (always returns, but low priority)."""
    return {
        "rule_id": "C2",
        "name": "no_major_issue",
        "priority": "low",
        "what_happened": "No major mechanical issue stood out on this swing.",
        "what_it_likely_means": "The swing was organized and functional relative to the current model.",
        "likely_effect": "Likely supports repeatable contact and better adjustability.",
        "coaching_focus": "Reinforce what is working.",
        "short_coaching_cue": "Keep repeating this move.",
    }


SHARED_RULES = [
    {"id": "C1", "applies_to": ["regular", "left_slap"], "fn": _rule_c1},
    {"id": "C2", "applies_to": ["regular", "left_slap"], "fn": _rule_c2},
]
