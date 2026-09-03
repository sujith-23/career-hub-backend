"""
Career Vision Hub — Backend API
Serves the career-path content (streams -> paths -> children) that used to be
hardcoded in the frontend's `DATA` object, plus click-tracking and a
student feedback/question endpoint.

Run locally:
    pip install -r requirements.txt
    python app/seed.py        # one-time: load data/seed_data.json into SQLite
    uvicorn app.main:app --reload

Docs available at /docs once running.
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from firebase_admin import auth

from . import models, schemas
from .database import SessionLocal, engine
from .firebase_auth import get_current_user, get_current_user_optional, require_admin

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Career Vision Hub API",
    description="Backend for the Career Vision Hub / Grama Vaani career-guidance site",
    version="1.0.0",
)

# Allow the GitHub Pages frontend (and local dev) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your GitHub Pages origin before going live
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


# ---------- Content endpoints (replace the hardcoded DATA object) ----------

@app.get("/api/streams", response_model=list[schemas.StreamSummary])
def list_streams(db: Session = Depends(get_db)):
    """Lightweight list for the hub screen: id, name, full, color, desc."""
    streams = db.query(models.Stream).all()
    return streams


@app.get("/api/streams/{stream_id}", response_model=schemas.StreamDetail)
def get_stream(stream_id: str, db: Session = Depends(get_db)):
    """Full stream detail including all paths, matching the old DATA[streamId] shape."""
    stream = db.query(models.Stream).filter(models.Stream.id == stream_id).first()
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")
    return stream


@app.get("/api/streams/full/all")
def get_all_streams_full(db: Session = Depends(get_db)):
    """
    Returns every stream keyed by id, in the exact shape the old frontend
    `DATA` object used (DATA[streamId] = {name, full, color, desc, paths}).
    One call instead of 11 — this is what the frontend should fetch on load.
    """
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

# ---------- Scholarship endpoints ----------

import json
from pathlib import Path

SCHOLARSHIPS_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "scholarships"
    / "scholarships_master.json"
)


@app.get("/api/scholarships")
def list_scholarships(
    search: str | None = None,
    education_level: str | None = None,
):
    """
    Return scholarships from the master scholarship dataset.

    Optional filters:
      search            - searches scholarship name/provider
      education_level  - filters by education level
    """

    if not SCHOLARSHIPS_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail="Scholarship dataset not found",
        )

    try:
        with open(SCHOLARSHIPS_FILE, "r", encoding="utf-8") as f:
            scholarships = json.load(f)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to read scholarship dataset: {str(e)}",
        )

    if not isinstance(scholarships, list):
        raise HTTPException(
            status_code=500,
            detail="Scholarship dataset must contain a list",
        )

    results = scholarships

    if search:
        search_lower = search.strip().lower()

        results = [
            scholarship
            for scholarship in results
            if search_lower in scholarship.get("name", "").lower()
            or search_lower in scholarship.get("provider", "").lower()
        ]

    if education_level:
        level_lower = education_level.strip().lower()

        results = [
            scholarship
            for scholarship in results
            if any(
                level_lower in str(level).lower()
                for level in scholarship.get("education_levels", [])
            )
        ]

    return {
        "total": len(results),
        "scholarships": results,
    }


@app.get("/api/scholarships/{scholarship_index}")
def get_scholarship(scholarship_index: int):
    """Return one scholarship by its zero-based index."""

    if not SCHOLARSHIPS_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail="Scholarship dataset not found",
        )

    try:
        with open(SCHOLARSHIPS_FILE, "r", encoding="utf-8") as f:
            scholarships = json.load(f)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to read scholarship dataset: {str(e)}",
        )

    if not isinstance(scholarships, list):
        raise HTTPException(
            status_code=500,
            detail="Scholarship dataset must contain a list",
        )

    if scholarship_index < 0 or scholarship_index >= len(scholarships):
        raise HTTPException(
            status_code=404,
            detail="Scholarship not found",
        )

    return scholarships[scholarship_index]
# ---------- Click / usage tracking ----------

@app.post("/api/track", response_model=schemas.TrackEventOut)
def track_event(
    event: schemas.TrackEventIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user_optional),
):
    """
    Log which stream/path/node was clicked, for analytics.
    If the student is logged in, their identity is recorded too (so Grama
    Vaani can see which student showed interest in which path); if not
    logged in, the click is still logged anonymously.
    """
    row = models.ClickEvent(
        stream_id=event.stream_id,
        path_id=event.path_id,
        node_id=event.node_id,
        user_id=user["uid"] if user else None,
        user_email=user["email"] if user else None,
        created_at=datetime.utcnow(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/api/analytics/popular", response_model=list[schemas.PopularItem])
def popular_items(
    limit: int = 10,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Most-clicked streams (aggregated, anonymous) — safe for any logged-in user to see."""
    from sqlalchemy import func

    results = (
        db.query(
            models.ClickEvent.stream_id,
            func.count(models.ClickEvent.id).label("clicks"),
        )
        .group_by(models.ClickEvent.stream_id)
        .order_by(func.count(models.ClickEvent.id).desc())
        .limit(limit)
        .all()
    )
    return [{"stream_id": r[0], "clicks": r[1]} for r in results]


@app.get("/api/analytics/students")
def student_interest(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    """
    ADMIN ONLY (email must be in the ADMIN_EMAILS env var).
    Shows which logged-in student explored which stream/path, and how many
    times — i.e. real per-student interest data, not just aggregated counts.
    Anonymous (not-logged-in) clicks are excluded here since there's no
    student to attribute them to.
    """
    from sqlalchemy import func

    rows = (
        db.query(
            models.ClickEvent.user_email,
            models.ClickEvent.stream_id,
            models.ClickEvent.path_id,
            func.count(models.ClickEvent.id).label("clicks"),
            func.max(models.ClickEvent.created_at).label("last_seen"),
        )
        .filter(models.ClickEvent.user_email.isnot(None))
        .group_by(models.ClickEvent.user_email, models.ClickEvent.stream_id, models.ClickEvent.path_id)
        .order_by(models.ClickEvent.user_email, func.count(models.ClickEvent.id).desc())
        .all()
    )

    by_student = {}
    for email, stream_id, path_id, clicks, last_seen in rows:
        by_student.setdefault(email, []).append({
            "stream_id": stream_id,
            "path_id": path_id,
            "clicks": clicks,
            "last_seen": last_seen.isoformat() if last_seen else None,
        })

    return by_student

# ---------- Personalized recommendations ----------

# ---------- Personalized recommendations ----------

# ---------- Personalized recommendations ----------

@app.get("/api/recommendations")
def personalized_recommendations(
    db: Session = Depends(get_db),
    user=Depends(get_current_user_optional),
):
    if not user:
        return []

    user_id = user.get("uid")

    if not user_id:
        return []

    from sqlalchemy import func

    # =========================================================
    # 1. GET ONLY THIS USER'S CLICK HISTORY
    # =========================================================

    history = (
        db.query(
            models.ClickEvent.stream_id,
            models.ClickEvent.path_id,
            models.ClickEvent.node_id,
            func.count(models.ClickEvent.id).label("clicks"),
            func.max(models.ClickEvent.created_at).label("last_seen"),
        )
        .filter(
            models.ClickEvent.user_id == user_id
        )
        .group_by(
            models.ClickEvent.stream_id,
            models.ClickEvent.path_id,
            models.ClickEvent.node_id,
        )
        .order_by(
            func.count(models.ClickEvent.id).desc()
        )
        .all()
    )

    if not history:
        return []

    # =========================================================
    # 2. LOAD STREAM DATA
    # =========================================================

    streams = db.query(models.Stream).all()

    # =========================================================
    # 3. BUILD LOOKUP FOR COURSE / CAREER NAMES
    # =========================================================

    node_lookup = {}

    def collect_nodes(
        stream_id,
        paths,
        parent_path=None,
    ):
        if not isinstance(paths, dict):
            return

        for item_id, item in paths.items():

            if not isinstance(item, dict):
                continue

            current_path = parent_path or item_id

            node_lookup[
                (
                    stream_id,
                    current_path,
                    item_id,
                )
            ] = {
                "name": item.get(
                    "name",
                    item_id,
                ),
                "desc": item.get(
                    "desc",
                    "Explore this career path.",
                ),
            }

            children = item.get("children")

            if children:
                collect_nodes(
                    stream_id,
                    children,
                    current_path,
                )

    for stream in streams:
        collect_nodes(
            stream.id,
            stream.paths,
        )

    # =========================================================
    # 4. BUILD RECOMMENDATIONS FROM MOST-CLICKED ITEMS
    # =========================================================

    recommendations = []

    for row in history:

        if not row.stream_id:
            continue

        clicks = int(row.clicks or 0)

        if clicks <= 0:
            continue

        key = (
            row.stream_id,
            row.path_id,
            row.node_id,
        )

        info = node_lookup.get(key)

        # If exact lookup isn't available, use node_id
        # as the display name.
        if info:
            name = info["name"]
            desc = info["desc"]
        else:
            name = row.node_id or row.path_id or row.stream_id
            desc = "Explore this career path."

        recommendations.append({
            "stream_id": row.stream_id,
            "path_id": row.path_id,
            "node_id": row.node_id,
            "name": name,
            "desc": desc,
            "clicks": clicks,
            "score": clicks,
        })

    # =========================================================
    # 5. SORT BY HIGHEST CLICKS
    # =========================================================

    recommendations.sort(
        key=lambda item: (
            item["clicks"],
            item["name"],
        ),
        reverse=True,
    )

    # =========================================================
    # 6. SHOW TOP 3
    # =========================================================

    recommendations = recommendations[:3]

    if not recommendations:
        return []

    # =========================================================
    # 7. CALCULATE MATCH %
    # =========================================================

    max_clicks = max(
        item["clicks"]
        for item in recommendations
    )

    min_clicks = min(
        item["clicks"]
        for item in recommendations
    )

    for item in recommendations:

        clicks = item["clicks"]

        if max_clicks == min_clicks:

            match = 90

        else:

            ratio = (
                (clicks - min_clicks)
                / (max_clicks - min_clicks)
            )

            match = round(
                80 + (ratio * 19)
            )

        item["match"] = match

        item["path"] = (
            f"#/{item['stream_id']}/"
            f"{item['path_id']}/"
            f"{item['node_id']}"
        )

    return recommendations

# ---------- Student feedback / "ask a mentor" ----------

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
    """Simple admin-facing list (add auth before exposing this publicly)."""
    return db.query(models.Feedback).order_by(models.Feedback.created_at.desc()).all()


# ---------- Saved paths (requires login) ----------

@app.post("/api/saved-paths", response_model=schemas.SavedPathOut)
def save_path(
    item: schemas.SavedPathIn,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    
    """Bookmark a career path for the logged-in student."""
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
    """Return saved career paths for the logged-in student."""
    return (
        db.query(models.SavedPath)
        .filter(models.SavedPath.user_id == user_id)
        .order_by(models.SavedPath.created_at.desc())
        .all()
    )


@app.get("/api/admin/saved-paths")
def admin_saved_paths(
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """
    ADMIN ONLY.
    Returns saved career paths grouped by student email.
    """

    rows = (
        db.query(models.SavedPath)
        .order_by(
            models.SavedPath.user_id,
            models.SavedPath.created_at.desc()
        )
        .all()
    )

    by_student = {}

    for row in rows:

        # Convert Firebase UID to student email
        try:
            firebase_user = auth.get_user(row.user_id)
            student_email = firebase_user.email or row.user_id
        except Exception:
            # If Firebase user cannot be found, keep UID
            student_email = row.user_id

        by_student.setdefault(student_email, []).append({
            "id": row.id,
            "stream_id": row.stream_id,
            "path_id": row.path_id,
            "node_id": row.node_id,
            "label": row.label,
            "created_at": (
                row.created_at.isoformat()
                if row.created_at else None
            ),
        })

    return by_student

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
# ---------- Student Profile ----------

@app.get("/api/profile", response_model=schemas.StudentProfileOut)
def get_profile(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Return the profile of the currently logged-in student."""

    row = (
        db.query(models.StudentProfile)
        .filter(models.StudentProfile.user_id == user_id)
        .first()
    )

    if not row:
        # Create a profile automatically for a new logged-in student
        try:
            firebase_user = auth.get_user(user_id)
            email = firebase_user.email
        except Exception:
            email = None

        row = models.StudentProfile(
            user_id=user_id,
            email=email,
            created_at=datetime.utcnow(),
        )

        db.add(row)
        db.commit()
        db.refresh(row)

    return row


@app.put("/api/profile", response_model=schemas.StudentProfileOut)
def update_profile(
    item: schemas.StudentProfileIn,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Update the currently logged-in student's profile."""

    row = (
        db.query(models.StudentProfile)
        .filter(models.StudentProfile.user_id == user_id)
        .first()
    )

    if not row:
        try:
            firebase_user = auth.get_user(user_id)
            email = firebase_user.email
        except Exception:
            email = None

        row = models.StudentProfile(
            user_id=user_id,
            email=email,
            created_at=datetime.utcnow(),
        )

        db.add(row)

    # Update profile fields
    row.name = item.name
    row.phone = item.phone
    row.school_name = item.school_name
    row.location = item.location
    row.marks = item.marks
    row.photo_url = item.photo_url

    db.commit()
    db.refresh(row)

    return row

# ---------- Education Finder ----------

@app.get(
    "/api/institutions",
    response_model=schemas.InstitutionListOut
)
def list_institutions(
    search: str | None = None,
    state: str | None = None,
    district: str | None = None,
    institution_type: str | None = None,
    university: str | None = None,
    level: str | None = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Search and paginate educational institutions across India."""

    page = max(page, 1)
    limit = min(max(limit, 1), 100)

    query = db.query(models.Institution)

    if search:
        query = query.filter(
            models.Institution.name.ilike(f"%{search}%")
        )

    if state:
        query = query.filter(
            models.Institution.state.ilike(f"%{state}%")
        )

    if district:
        query = query.filter(
            models.Institution.district.ilike(f"%{district}%")
        )

        if institution_type:
            query = query.filter(
                models.Institution.institution_type.ilike(
                    f"%{institution_type}%"
                )
            )

    if university:
        query = query.filter(
            models.Institution.university.ilike(
                f"%{university}%"
            )
        )

    if level:
        query = query.filter(
            models.Institution.level.ilike(f"%{level}%")
        )

    total = query.count()

    offset = (page - 1) * limit

    items = (
        query
        .order_by(models.Institution.name.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "items": items,
    }

@app.get(
    "/api/institutions/{institution_id}",
    response_model=schemas.InstitutionOut
)
def get_institution(
    institution_id: int,
    db: Session = Depends(get_db),
):
    """Return details for one educational institution."""

    institution = (
        db.query(models.Institution)
        .filter(models.Institution.id == institution_id)
        .first()
    )

    if not institution:
        raise HTTPException(
            status_code=404,
            detail="Institution not found"
        )

    return institution