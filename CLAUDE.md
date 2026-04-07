# Scout Stream - Softball Hitting Biomechanics MVP

## Project Overview
Coach-first softball swing analysis platform using markerless motion capture (MediaPipe/FreeMoCap) to analyze hitting mechanics for regular and left-handed slap hitters.

## Tech Stack
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0, Celery, Redis
- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Database**: PostgreSQL
- **Motion Processing**: MediaPipe Pose (MVP), FreeMoCap (future multi-camera)

## Development Commands
```bash
# Backend
cd backend && pip install -e ".[dev]"
cd backend && uvicorn app.main:app --reload
cd backend && celery -A processing.worker worker --loglevel=info
cd backend && pytest

# Frontend
cd frontend && npm install
cd frontend && npm run dev

# Infrastructure
docker compose up -d  # PostgreSQL + Redis
```

## Key Architecture
- `backend/app/` - FastAPI application (models, schemas, API routes)
- `backend/processing/` - Motion pipeline (landmark extraction, event detection, metrics, interpretation)
- `frontend/src/` - Next.js coach-facing web app

## Core Concepts
- **Events**: Start (last quiet frame), Launch (first committed attack), Contact (impact frame)
- **Metrics**: spine angle, spine position, foot angles, hip angle, shoulder angle, separation
- **Plant**: Full-foot stable plant (heel down) - used internally for event logic, not exposed in MVP UI
- **Swing Types**: regular, left_slap (MVP); power_slap, drag, bunt (future)

## Branch
Develop on: `claude/softball-biomechanics-mvp-uTGit`
