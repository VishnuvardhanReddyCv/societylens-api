from datetime import datetime

from pydantic import BaseModel

from app.models.issue import IssueStatus


class IssueCreate(BaseModel):
    title: str
    description: str


class IssueUpdate(BaseModel):
    status: IssueStatus


class IssueOut(BaseModel):
    id: str
    title: str
    description: str
    status: IssueStatus
    raised_by: str
    complex_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
