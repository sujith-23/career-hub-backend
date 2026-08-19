from sqlalchemy import Column, String, Integer, DateTime, JSON
from .database import Base


class Stream(Base):
    __tablename__ = "streams"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    full = Column(String, nullable=False)
    color = Column(String, nullable=True)
    desc = Column(String, nullable=True)
    paths = Column(JSON, nullable=False, default=dict)


class ClickEvent(Base):
    __tablename__ = "click_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stream_id = Column(String, index=True, nullable=False)
    path_id = Column(String, nullable=True)
    node_id = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    contact = Column(String, nullable=True)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)


class SavedPath(Base):
    __tablename__ = "saved_paths"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, index=True, nullable=False)
    stream_id = Column(String, nullable=False)
    path_id = Column(String, nullable=True)
    node_id = Column(String, nullable=True)
    label = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)