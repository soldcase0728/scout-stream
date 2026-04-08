# Scout Stream

Softball hitting biomechanics MVP. Coach-first swing analysis platform using markerless motion capture to analyze regular hitting and left-handed slap hitting.

Upload a swing video, get automatic event detection (Start / Launch / Contact), body position metrics, coaching interpretation, and drill recommendations.

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose

## Quick Start

```bash
# 1. Install dependencies
make setup

# 2. Start PostgreSQL + Redis, run migrations
make db

# 3. Create test account
make seed

# 4. Start backend API (in a new terminal)
make backend

# 5. Start Celery worker (in a new terminal)
make worker

# 6. Start frontend (in a new terminal)
make frontend
```

Open http://localhost:3000 and log in with:
- Email: `test@scoutstream.com`
- Password: `password123`

## Manual Setup (without Make)

```bash
# Copy env file
cp .env.example .env

# Install backend
cd backend && pip install -e ".[dev]"

# Install frontend
cd frontend && npm install

# Start infrastructure
docker compose up -d

# Run database migrations
cd backend && alembic upgrade head

# Seed test data
cd backend && python -m scripts.seed_data

# Start backend (terminal 1)
cd backend && uvicorn app.main:app --reload

# Start Celery worker (terminal 2)
cd backend && celery -A processing.worker worker --loglevel=info

# Start frontend (terminal 3)
cd frontend && npm run dev
```

## Architecture

```
Frontend (Next.js :3000)  ->  Backend API (FastAPI :8000)  ->  Celery Workers
                                      |                            |
                                 PostgreSQL                   MediaPipe Pose
                                   Redis                    Event Detection
                                                           Metrics Engine
                                                       Interpretation Engine
```

### Processing Pipeline

1. **Video Upload** - Coach uploads swing video through the UI
2. **Landmark Extraction** - MediaPipe Pose extracts 14 body landmarks per frame
3. **Event Detection** - Automatically identifies Start, Launch, Contact frames
4. **Metrics Computation** - Spine angle/position, foot angles, hip angle, shoulder angle, separation at each checkpoint
5. **Coaching Interpretation** - 12 rules-based engine generates "what happened / what it means / what to coach next"
6. **Drill Recommendations** - Maps triggered rules to specific corrective drills

### Swing Types
- **Regular** - Full swing (right or left-handed)
- **Left Slap** - Left-handed slap hitting with crossover movement

## Key Pages

| URL | Description |
|-----|-------------|
| `/` | Dashboard |
| `/athletes` | Athlete management |
| `/athletes/[id]` | Athlete detail + session history |
| `/athletes/[id]/trends` | Metric trends over time |
| `/sessions/[id]` | Session detail + video upload |
| `/swings/[id]` | Swing viewer (metrics, interpretation, drills) |
| `/swings/compare?a=X&b=Y` | Side-by-side comparison |
| `/guide` | Recording instructions for coaches |

## Tests

```bash
make test
# or
cd backend && pytest -v
```

## Documentation

See `docs/` for detailed specifications:
- [Product Requirements](docs/prd.md)
- [Metric Specification](docs/metric_spec.md)
- [Event Detection](docs/event_detection_spec.md)
- [Interpretation Rules](docs/interpretation_rules.md)
- [Labeling Protocol](docs/labeling_protocol.md)
