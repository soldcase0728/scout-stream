"""Interpretation engine.

Runs coaching rules against swing metrics, ranks results,
and generates a concise summary a coach can use immediately.

Output for each swing:
  - what_happened (1-2 sentences)
  - what_it_means (1 sentence)
  - what_to_coach_next (1 sentence)
  - rules_triggered (list of rule dicts)
  - severity (high/medium/low)
"""

from __future__ import annotations

from processing.rules import ALL_RULES

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def interpret_swing(
    metrics: dict, deltas: dict, timing: dict, swing_type: str = "regular"
) -> dict:
    """Run all applicable rules and generate coaching summary."""
    triggered = []

    for rule_def in ALL_RULES:
        if swing_type not in rule_def["applies_to"]:
            continue
        result = rule_def["fn"](metrics, deltas, timing)
        if result:
            triggered.append(result)

    # Sort by priority
    triggered.sort(key=lambda r: PRIORITY_ORDER.get(r["priority"], 2))

    # Filter: show top 1 high or top 2 medium, suppress C2 if others exist
    real_issues = [r for r in triggered if r["rule_id"] != "C2"]

    if real_issues:
        display = _select_display_rules(real_issues)
        severity = display[0]["priority"]
    else:
        # No real issues - use C2
        c2 = [r for r in triggered if r["rule_id"] == "C2"]
        display = c2[:1] if c2 else []
        severity = "low"

    summary = _build_summary(display)

    return {
        "what_happened": summary["what_happened"],
        "what_it_means": summary["what_it_means"],
        "what_to_coach_next": summary["what_to_coach_next"],
        "rules_triggered": [
            {"rule_id": r["rule_id"], "name": r["name"], "priority": r["priority"]}
            for r in triggered
        ],
        "severity": severity,
    }


def _select_display_rules(rules: list[dict]) -> list[dict]:
    """Select rules to display to coach. Avoid flooding."""
    high = [r for r in rules if r["priority"] == "high"]
    medium = [r for r in rules if r["priority"] == "medium"]

    if high:
        # Show top high rule, maybe one supporting medium
        result = high[:1]
        if medium:
            result.append(medium[0])
        return result
    elif medium:
        return medium[:2]
    else:
        return rules[:2]


def _build_summary(display_rules: list[dict]) -> dict:
    """Combine display rules into concise coaching summary."""
    if not display_rules:
        return {
            "what_happened": "No significant mechanical patterns detected.",
            "what_it_means": "The swing appears functional.",
            "what_to_coach_next": "Continue reinforcing current mechanics.",
        }

    primary = display_rules[0]

    what_happened = primary["what_happened"]
    if len(display_rules) > 1:
        what_happened += f" {display_rules[1]['what_happened']}"

    what_it_means = primary["what_it_likely_means"]
    what_to_coach_next = primary["coaching_focus"]

    return {
        "what_happened": what_happened,
        "what_it_means": what_it_means,
        "what_to_coach_next": what_to_coach_next,
    }
