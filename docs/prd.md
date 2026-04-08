# Product Requirements Document - Scout Stream MVP

## Objective
Coach-first softball swing analysis platform using markerless motion capture to improve regular hitting and left-handed slap hitting.

## MVP Scope

### In Scope
- Athlete profiles, session management
- Swing video upload and async processing
- Event detection: Start, Launch, Contact
- Metrics: spine angle/position, foot angles, hip angle, shoulder angle, separation
- Rules-based coaching interpretation (12 rules)
- Manual event frame adjustment with recomputation
- Side-by-side swing comparison
- Athlete metric trends over time
- Drill recommendations linked to coaching rules
- Recording guidance for coaches

### Out of Scope (MVP)
- Real-time feedback, bat tracking, ball tracking
- Wearable/force plate integration
- Recruiting analytics, injury prediction
- Athlete-facing mobile app

## Users
- **Primary**: Private softball instructors, travel-ball coaches
- **Secondary**: High school programs
- **Tertiary**: College programs

## Core Workflow
1. Coach creates athlete and session
2. Uploads swing video
3. System processes: landmarks -> events -> metrics -> interpretation
4. Coach reviews event frames (can adjust)
5. Reads coaching summary, metrics, drill recommendations
6. Saves notes, compares to prior swings

## Supported Swing Types
- Regular swing (MVP)
- Left slap (MVP)
- Power slap, drag, bunt (future)

## Success Criteria
- Coach can upload 5 swings and get feedback in minutes
- Trusts Start/Launch/Contact frames enough to use them
- Receives softball-specific coaching output
- Can track progress over time

## Tech Stack
- Backend: Python, FastAPI, SQLAlchemy, Celery, Redis
- Frontend: Next.js, React, TypeScript, Tailwind
- Database: PostgreSQL
- Motion: MediaPipe Pose (MVP), FreeMoCap (future multi-camera)
