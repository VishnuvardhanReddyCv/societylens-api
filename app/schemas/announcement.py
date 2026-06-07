from datetime import datetime

from pydantic import BaseModel


class AnnouncementCreate(BaseModel):
    title: str
    body: str


class AnnouncementOut(BaseModel):
    id: str
    title: str
    body: str
    created_by: str
    complex_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
