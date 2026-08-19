"""
Career Vision Hub — Backend API
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime

from . import models, schemas
from .database import SessionLocal, engine
from .firebase_auth import get_current_user

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Career Vision Hub API",
    description="Backend for the Career Vision Hub / Grama Vaani career-guidance site",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"status": "ok", "service": "career-vision-hub-api"}


@app.get("/api/streams", response_model=list[schemas.StreamSummary])
def list_streams(db: Session = Depends(get_db)):
    streams = db.query(models.Stream).all()
    return streams


@app.get("/api/streams/{stream_id}", response_model=schemas.StreamDetail)
def get_stream(stream_id: str, db: Session = Depends(get_db)):
    stream = db.query(models.Stream).filter(models.Stream.id == stream_id).first()
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")
    return stream


@app.get("/api/streams/full/all")
def get_all_streams_full(db: Session = Depends(get_db)):
    streams = db.query(models.Stream).all()
    return {
        s.id: {
            "name": s.name,
            "full": s.full,
            "color": s.color,
            "desc": s.desc,
            "paths": s.paths,
        }
        for s in streams
    }


@app.post("/api/track", response_model=schemas.TrackEventOut)
def track_event(event: schemas.TrackEventIn, db: Session = Depends(get_db)):
    row = models.ClickEvent(
        stream_id=event.stream_id,
        path_id=event.path_id,
        node_id=event.node_id,
        created_at=datetime.utcnow(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/api/analytics/popular", response_model=list[schemas.PopularItem])
def popular_items(limit: int = 10, db: Session = Depends(get_db)):
    from sqlalchemy import func
    results = (
        db.query(models.ClickEvent.stream_id, func.count(models.ClickEvent.id).label("clicks"))
        .group_by(models.ClickEvent.stream_id)
        .order_by(func.count(models.ClickEvent.id).desc())
        .limit(limit)
        .all()
    )
    return [{"stream_id": r[0], "clicks": r[1]} for r in results]


@app.post("/api/feedback", response_model=schemas.FeedbackOut)
def submit_feedback(item: schemas.FeedbackIn, db: Session = Depends(get_db)):
    row = models.Feedback(
        name=item.name,
        contact=item.contact,
        message=item.message,
        created_at=datetime.utcnow(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/api/feedback", response_model=list[schemas.FeedbackOut])
def list_feedback(db: Session = Depends(get_db)):
    return db.query(models.Feedback).order_by(models.Feedback.created_at.desc()).all()


@app.post("/api/saved-paths", response_model=schemas.SavedPathOut)
def save_path(
    item: schemas.SavedPathIn,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    row = models.SavedPath(
        user_id=user_id,
        stream_id=item.stream_id,
        path_id=item.path_id,
        node_id=item.node_id,
        label=item.label,
        created_at=datetime.utcnow(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/api/saved-paths", response_model=list[schemas.SavedPathOut])
def list_saved_paths(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    return (
        db.query(models.SavedPath)
        .filter(models.SavedPath.user_id == user_id)
        .order_by(models.SavedPath.created_at.desc())
        .all()
    )


@app.delete("/api/saved-paths/{saved_id}")
def delete_saved_path(
    saved_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    row = (
        db.query(models.SavedPath)
        .filter(models.SavedPath.id == saved_id, models.SavedPath.user_id == user_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Saved path not found")
    db.delete(row)
    db.commit()
    return {"deleted": saved_id}