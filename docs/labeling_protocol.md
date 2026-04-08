# Labeling Protocol for Start, Launch, Contact

## Purpose
Consistent human-reviewed event labels drive metric accuracy and rule reliability.

## Process
1. Watch swing at full speed
2. Watch at reduced speed
3. Mark **Start** first
4. Mark **Contact** second (usually easier to anchor)
5. Mark **Launch** last (with Start and Contact set, easier to place)
6. Scrub 1-3 frames around each selection to confirm
7. Save final labels

## Start
- **Choose**: Last quiet, stable frame before meaningful movement
- **Not**: First frame of clip, or after movement has begun
- **Slappers**: Before crossover begins, not after travel starts

## Launch
- **Choose**: First committed attack frame (gather-to-go transition)
- **Not**: During gather, or halfway through delivery
- **Slappers**: When delivery intent begins, not just movement into the box
- **If ambiguous**: Choose earliest defensible committed frame

## Contact
- **Choose**: Frame nearest actual/intended impact
- **Not**: Follow-through or pre-contact
- **Dry swings**: Intended contact frame (mark as estimated)

## Ordering Rule
`Start < Launch < Contact` (always)

## Quality Flags
- `reviewer_confidence`: high / medium / low
- `estimated_contact`: yes / no
- `late_start_clip`: yes / no
- `unreviewable`: yes / no

## Inter-Rater Calibration
- 2-3 reviewers label same 25-50 swings initially
- Compare frame differences, discuss disagreements
- Launch is hardest to align - focus calibration there

## Gold Standard Set
- 200-500 reviewed swings (regular + left slap)
- Multiple athletes, environments
- Frozen for regression testing
