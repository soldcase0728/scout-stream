"""Seed script: creates a test coach, athlete, and session for local development.

Run with: python -m scripts.seed_data
"""

from app.database import SessionLocal, engine, Base
from app.models.coach import Coach
from app.models.athlete import Athlete
from app.models.session import Session
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

COACH_EMAIL = "test@scoutstream.com"
COACH_PASSWORD = "password123"
COACH_NAME = "Test Coach"


def seed():
    db = SessionLocal()
    try:
        # Check if already seeded
        existing = db.query(Coach).filter(Coach.email == COACH_EMAIL).first()
        if existing:
            print(f"Seed data already exists (coach: {COACH_EMAIL})")
            print(f"Login at http://localhost:3000/login")
            print(f"  Email:    {COACH_EMAIL}")
            print(f"  Password: {COACH_PASSWORD}")
            return

        # Create coach
        coach = Coach(
            email=COACH_EMAIL,
            name=COACH_NAME,
            password_hash=pwd_context.hash(COACH_PASSWORD),
        )
        db.add(coach)
        db.flush()

        # Create sample athletes
        athlete1 = Athlete(
            coach_id=coach.id,
            first_name="Jane",
            last_name="Doe",
            handedness="right",
            primary_swing_type="regular",
            notes="Strong contact hitter, working on hip-shoulder separation",
        )
        athlete2 = Athlete(
            coach_id=coach.id,
            first_name="Sarah",
            last_name="Smith",
            handedness="left",
            primary_swing_type="left_slap",
            notes="Quick slapper, needs work on crossover efficiency and plant stability",
        )
        db.add(athlete1)
        db.add(athlete2)
        db.flush()

        # Create sample sessions
        session1 = Session(
            athlete_id=athlete1.id,
            coach_id=coach.id,
            session_type="practice",
            notes="Tee work - focusing on posture through contact",
        )
        session2 = Session(
            athlete_id=athlete2.id,
            coach_id=coach.id,
            session_type="practice",
            notes="Slap hitting rhythm drills",
        )
        db.add(session1)
        db.add(session2)

        db.commit()

        print("=" * 50)
        print("Seed data created successfully!")
        print("=" * 50)
        print()
        print(f"Coach:    {COACH_NAME}")
        print(f"Email:    {COACH_EMAIL}")
        print(f"Password: {COACH_PASSWORD}")
        print()
        print("Athletes:")
        print(f"  - {athlete1.first_name} {athlete1.last_name} (right / regular)")
        print(f"  - {athlete2.first_name} {athlete2.last_name} (left / left_slap)")
        print()
        print("Sessions created for both athletes.")
        print()
        print("Login at http://localhost:3000/login")
        print("Upload a swing video to test the full pipeline.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
