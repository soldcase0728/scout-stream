# Event Detection Specification

## Events

### Start
- **Definition**: Last quiet, stable frame before meaningful movement begins
- **Logic**: Find last frame where pelvis + shoulder speed are below threshold, before coordinated movement exceeds threshold
- **Regular hitters**: Just before load or stride initiation
- **Slappers**: Last stable frame before crossover begins

### Plant (internal only)
- **Definition**: First frame where lead foot is fully down (heel included), stable enough to accept force
- **Rule**: Toe touch does NOT count. Must be full-foot stable plant with heel down.
- **Not exposed in MVP UI** but used internally for event detection logic

### Launch
- **Definition**: First committed attack frame - transition from gather to delivery
- **Logic**: First frame after/near plant where pelvis angular velocity + wrist speed begin sustained increase
- **Regular hitters**: Near front-side stabilization, when delivery begins
- **Slappers**: When crossover/run converts into swing delivery intent (not just movement)

### Contact
- **Definition**: Estimated bat-ball impact frame
- **Logic**: Peak wrist speed after launch, or visible ball contact frame
- **Fallback**: Coach-correctable estimated contact for tee/dry swings

## Ordering
`Start < Plant <= Launch < Contact` (Plant optional)

## Confidence Scoring (0-1)
Higher when:
- Clear velocity difference between start and launch regions
- Reasonable launch-to-contact timing (5-30 frames)
- Clear wrist speed peak at contact

## Manual Override
- Coach can adjust all three event frames
- Adjustment triggers metric recomputation
- Both auto and final frames stored
