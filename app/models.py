from sqlalchemy import Column, String, Integer, DateTime, JSON
from .database import Base


class Stream(Base):
    """
    One row per top-level stream (mpc, bipc, mec, cec, hec, polytechnic, iti,
    vocational, skilldev, defence, govtjobs).

    `paths` stores the full nested paths/children structure as JSON, exactly
    like the old frontend DATA[streamId].paths object. This keeps the model
    simple while still letting an admin edit deeply nested content freely.
    If you outgrow this later, paths/children can be split into their own
    tables.
    """
    __tablename__ = "streams"

    id = Column(String, primary_key=True, index=True)   # e.g. "mpc"
    name = Column(String, nullable=False)                 # "MPC"
    full = Column(String, nullable=False)                 # "Maths, Physics, Chemistry"
    color = Column(String, nullable=True)                 # "var(--line-mpc)"
    desc = Column(String, nullable=True)
    paths = Column(JSON, nullable=False, default=dict)     # nested paths object


class ClickEvent(Base):
    __tablename__ = "click_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stream_id = Column(String, index=True, nullable=False)
    path_id = Column(String, nullable=True)
    node_id = Column(String, nullable=True)
    user_id = Column(String, index=True, nullable=True)     # Firebase UID, if logged in
    user_email = Column(String, nullable=True)               # for readable admin view
    created_at = Column(DateTime, nullable=False)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    contact = Column(String, nullable=True)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)


class SavedPath(Base):
    """A career path a logged-in student has bookmarked."""
    __tablename__ = "saved_paths"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, index=True, nullable=False)  # Firebase UID
    stream_id = Column(String, nullable=False)
    path_id = Column(String, nullable=True)
    node_id = Column(String, nullable=True)
    label = Column(String, nullable=True)  # human-readable name for display
    created_at = Column(DateTime, nullable=False)
class StudentProfile(Base):
    """Profile information for a logged-in student."""
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)

class Institution(Base):
    """Institution information for the India-wide Education Finder."""
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # AISHE identification
    aishe_code = Column(String, nullable=True, unique=True, index=True)

    # Basic information
    name = Column(String, nullable=False, index=True)

    # Location
    state = Column(String, nullable=False, index=True)
    district = Column(String, nullable=True, index=True)
    city = Column(String, nullable=True, index=True)
    address = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    location = Column(String, nullable=True, index=True)  # Rural / Urban

    # Institution information
    institution_type = Column(String, nullable=True, index=True)
    management = Column(String, nullable=True, index=True)

    # University information
    university_aishe_code = Column(String, nullable=True, index=True)
    university = Column(String, nullable=True, index=True)
    university_type = Column(String, nullable=True, index=True)

    # Additional information
    status = Column(String, nullable=True, index=True)
    level = Column(String, nullable=True, index=True)
    established_year = Column(Integer, nullable=True)
    website = Column(String, nullable=True)

    # Data source
    source = Column(String, nullable=True, index=True)

    created_at = Column(DateTime, nullable=False)
