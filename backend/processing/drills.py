"""Drill recommendation library.

Maps coaching rule IDs to specific corrective drills.
Each drill has a name, description, and target focus.
"""

from __future__ import annotations

DRILL_DATABASE: dict[str, list[dict]] = {
    "R1": [
        {
            "name": "Launch-to-Contact Posture Hold",
            "description": "Tee work. Take swing but freeze at contact position. Coach checks trunk angle matches launch position. Hold 3 seconds. 10 reps.",
            "focus": "Maintain trunk angle from launch through contact zone",
        },
        {
            "name": "Connection Ball Swings",
            "description": "Place a small ball between lead arm and torso. Swing without dropping it. Forces connected posture through delivery.",
            "focus": "Prevent posture rise and upper-body takeover",
        },
    ],
    "R2": [
        {
            "name": "Hip Lead Drill",
            "description": "From stance, stride and rotate hips to open while keeping shoulders closed. Hold the stretch for 2 seconds. Then finish swing. 15 reps.",
            "focus": "Train hips to lead shoulders in the sequence",
        },
        {
            "name": "Resistance Band Separation",
            "description": "Attach light band around torso. Stride and rotate hips against resistance while keeping shoulders back. Build separation feel.",
            "focus": "Develop hip-shoulder separation at launch",
        },
    ],
    "R3": [
        {
            "name": "Ground-Up Progression",
            "description": "Start from knees. Hit off tee using only lower body rotation. Progress to standing. Focus on feeling force start from the ground.",
            "focus": "Build lower-half engagement and force transfer",
        },
    ],
    "R4": [
        {
            "name": "Gather Drill",
            "description": "Place a line on the ground at stance position. Load and gather without crossing it. Stride only when coach calls. 10 reps.",
            "focus": "Control forward drift during load phase",
        },
    ],
    "R5": [
        {
            "name": "Line Drill - Foot Direction",
            "description": "Place tape on the ground as target line. Stride to land on or slightly closed to the line. Hit off tee. Check foot angle after each swing.",
            "focus": "Improve front-side foot direction at plant",
        },
    ],
    "R6": [
        {
            "name": "Posture Checkpoint Tee Work",
            "description": "Set up two tees at different heights. Hit the low tee while maintaining posture that could reach the high tee. Trains shape through contact.",
            "focus": "Maintain body organization through the strike zone",
        },
    ],
    "S1": [
        {
            "name": "Low Crossover Rhythm Drill",
            "description": "Set a visual height marker (bat held at shoulder level). Crossover and move through the box keeping head below the marker. 10 reps.",
            "focus": "Stay low and athletic through movement into delivery",
        },
        {
            "name": "Cone Depth Drill",
            "description": "Place cones at crossover start and plant position. Move through cones staying in athletic position. Add tee hit at the end.",
            "focus": "Control vertical rise during crossover",
        },
    ],
    "S2": [
        {
            "name": "Plant and Hold Drill",
            "description": "Crossover into firm plant. Hold at plant for 1 beat with shoulders still quiet. Then deliver. Trains upper-body patience.",
            "focus": "Keep upper body organized until delivery phase",
        },
    ],
    "S3": [
        {
            "name": "Directional Plant Drill",
            "description": "Mark three foot-angle targets on the ground. Crossover and plant on each target. Hit directional slap from each. Focus on controlling foot openness.",
            "focus": "Control front-side direction at plant for slappers",
        },
    ],
    "S4": [
        {
            "name": "Organized Launch Progression",
            "description": "Crossover to plant. At plant, coach checks hip-shoulder separation. Only swing if organized. Reject and reset if body is one block.",
            "focus": "Build clean transition from movement to delivery",
        },
    ],
    "S5": [
        {
            "name": "Short Box Tempo Drill",
            "description": "Shorten the crossover distance by 50%. Focus on quick, controlled movement to firm plant. Progress distance as control improves.",
            "focus": "Reduce excessive drift and improve movement control",
        },
    ],
    "C1": [
        {
            "name": "Early Rhythm Drill",
            "description": "Coach gives timing cue. Hitter must start earlier and create more usable time between launch and contact. Front toss with verbal timing.",
            "focus": "Expand the attack window for better adjustability",
        },
    ],
}


def get_drills_for_rules(rule_ids: list[str]) -> list[dict]:
    """Return drill recommendations for a list of triggered rule IDs."""
    drills = []
    seen = set()
    for rule_id in rule_ids:
        for drill in DRILL_DATABASE.get(rule_id, []):
            if drill["name"] not in seen:
                drills.append({**drill, "from_rule": rule_id})
                seen.add(drill["name"])
    return drills[:4]  # Limit to 4 drills max
