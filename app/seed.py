"""
One-time (or re-runnable) script to load data/seed_data.json into the DB.
Run with:  python -m app.seed
"""
import json
import os
from .database import SessionLocal, engine, Base
from . import models

Base.metadata.create_all(bind=engine)

SEED_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "seed_data.json")


def seed():
    with open(SEED_PATH, encoding="utf-8") as f:
        data = json.load(f)

    db = SessionLocal()
    try:
        for stream_id, stream in data.items():
            existing = db.query(models.Stream).filter(models.Stream.id == stream_id).first()
            row = existing or models.Stream(id=stream_id)
            row.name = stream.get("name", stream_id)
            row.full = stream.get("full", "")
            row.color = stream.get("color")
            row.desc = stream.get("desc")
            row.paths = stream.get("paths", {})
            if not existing:
                db.add(row)
        db.commit()
        print(f"Seeded {len(data)} streams into the database.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
