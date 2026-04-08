# Interpretation Rules Specification

## Output Format
Each swing produces:
- `what_happened` (1-2 sentences)
- `what_it_means` (1 sentence)
- `what_to_coach_next` (1 sentence)
- `rules_triggered` (list with rule_id, name, priority)
- `severity` (high/medium/low)

## Display Logic
- Show top 1 high-priority rule + 1 supporting medium
- Or up to 2 medium rules
- Suppress C2 (no issue) if real issues exist

## Regular Hitter Rules

| Rule | Name | Priority | Trigger |
|------|------|----------|---------|
| R1 | Late posture rise | High | Spine angle change >8° or spine Y change >0.03 from launch to contact |
| R2 | Early shoulder opening | High | Shoulder angle >20° at launch or separation <3° |
| R3 | Weak lower-half sequence | High | Hip delta <5° start-to-launch and separation <4° at launch |
| R4 | Excessive forward leak | Medium | Spine position X drift >0.05 start-to-launch |
| R5 | Front side too open | Medium | Lead foot >25° and hip >15° at launch |
| R6 | Contact posture collapse | Medium | Spine delta >10° and separation delta >8° launch-to-contact |

## Slap Hitter Rules

| Rule | Name | Priority | Trigger |
|------|------|----------|---------|
| S1 | Rising through movement | High | Spine Y rise >0.02 start-to-launch AND >0.01 launch-to-contact |
| S2 | Early upper-body takeover | High | Shoulder angle >18° and separation <4° at launch |
| S3 | Over-open front side | High | Lead foot >22° and hip >14° at launch |
| S4 | Weak delivery organization | High | Separation <3° and hip delta <4° at launch |
| S5 | Excessive drift | Medium | Spine X drift >0.06 or Z drift >0.04 start-to-launch |

## Shared Rules

| Rule | Name | Priority | Trigger |
|------|------|----------|---------|
| C1 | Timing compressed | Medium | Launch-to-contact <6 frames |
| C2 | No major issue | Low | No other rules triggered |

## Threshold Philosophy
- Layer 1: Fixed default thresholds (MVP)
- Layer 2: Swing-type-specific bands (future)
- Layer 3: Athlete baseline comparison (future)
