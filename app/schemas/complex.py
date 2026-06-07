from datetime import datetime

from pydantic import BaseModel


class ComplexOut(BaseModel):
    id: str
    name: str
    address: str
    city: str
    invite_code: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ComplexUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    city: str | None = None
