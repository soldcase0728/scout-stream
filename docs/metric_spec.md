# Metric Specification

## Coordinate System
- X = forward-back (toward pitcher)
- Y = vertical (MediaPipe: lower Y = higher position)
- Z = lateral

## Checkpoint Metrics (computed at Start, Launch, Contact)

### Spine Angle
- **Definition**: Angle of trunk segment (pelvis midpoint to shoulder midpoint) relative to vertical
- **Landmarks**: left_hip, right_hip, left_shoulder, right_shoulder
- **Units**: degrees
- **Coaching meaning**: Changes indicate posture loss or rising

### Spine Angle Side
- **Definition**: Trunk side bend in frontal plane
- **Landmarks**: Same as spine angle
- **Units**: degrees

### Spine Position (X, Y, Z)
- **Definition**: Pelvis midpoint location in 3D space
- **Units**: normalized MediaPipe coordinates
- **Coaching meaning**: Forward drift, vertical rise, lateral instability

### Lead Foot Angle
- **Definition**: Orientation of lead foot (heel to toe) relative to forward direction
- **Landmarks**: lead heel, lead foot index (toe)
- **Units**: degrees (positive = open, negative = closed)
- **Lead side**: Left foot for right-handed, right foot for left-handed

### Rear Foot Angle
- **Definition**: Same as lead foot but for rear foot
- **Landmarks**: rear heel, rear foot index

### Hip Angle
- **Definition**: Pelvis rotation in horizontal plane relative to target line
- **Landmarks**: left_hip, right_hip
- **Units**: degrees (positive = open)

### Shoulder Angle
- **Definition**: Shoulder line rotation in horizontal plane
- **Landmarks**: left_shoulder, right_shoulder
- **Units**: degrees (positive = open)

### Shoulder Tilt
- **Definition**: Vertical tilt of shoulder line
- **Units**: degrees

### Separation
- **Definition**: Shoulder angle minus hip angle
- **Formula**: `separation = shoulder_angle - hip_angle`
- **Coaching meaning**: Measures hip-shoulder sequence quality

## Delta Metrics
Computed between: Start→Launch, Launch→Contact, Start→Contact
For each checkpoint metric: `delta = value_at_B - value_at_A`

## Timing Metrics
- `frames_start_to_launch`
- `frames_launch_to_contact`
- `frames_start_to_contact`

## Quality Fields
- `landmark_confidence`: Mean visibility score (0-1)
- `event_confidence`: Event detection confidence (0-1)
