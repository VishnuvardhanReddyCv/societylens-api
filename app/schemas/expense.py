from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.expense import ExpenseCategory, VoteValue


class ExpenseCreate(BaseModel):
    title: str
    description: str | None = None
    amount: Decimal
    category: ExpenseCategory
    receipt_url: str | None = None


class VoteOut(BaseModel):
    id: str
    value: VoteValue
    user_id: str

    model_config = {"from_attributes": True}


class ExpenseOut(BaseModel):
    id: str
    title: str
    description: str | None
    amount: Decimal
    category: ExpenseCategory
    receipt_url: str | None
    created_by: str
    created_at: datetime
    approve_count: int = 0
    reject_count: int = 0
    my_vote: str | None = None

    model_config = {"from_attributes": True}


class VoteRequest(BaseModel):
    value: VoteValue
