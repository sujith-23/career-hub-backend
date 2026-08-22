from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class StreamSummary(BaseModel):
    id: str
    name: str
    full: str
    color: Optional[str] = None
    desc: Optional[str] = None

    class Config:
        from_attributes = True


class StreamDetail(StreamSummary):
    paths: dict[str, Any]

    class Config:
        from_attributes = True


class TrackEventIn(BaseModel):
    stream_id: str
    path_id: Optional[str] = None
    node_id: Optional[str] = None


class TrackEventOut(TrackEventIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PopularItem(BaseModel):
    stream_id: str
    clicks: int


class FeedbackIn(BaseModel):
    name: Optional[str] = None
    contact: Optional[str] = None
    message: str


class FeedbackOut(FeedbackIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SavedPathIn(BaseModel):
    stream_id: str
    path_id: Optional[str] = None
    node_id: Optional[str] = None
    label: Optional[str] = None


class SavedPathOut(SavedPathIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
class StudentProfileIn(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None


class StudentProfileOut(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True
