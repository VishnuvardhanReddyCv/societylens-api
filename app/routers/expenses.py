from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.expense import ExpenseCreate, VoteRequest
from app.models.expense import ExpenseCategory
from app.models.user import User
from app.core.dependencies import get_current_user, require_admin
from app.services import expense_service

router = APIRouter(prefix="/api/expenses", tags=["expenses"])


def _serialize_expense(e, approve: int, reject: int, my_vote) -> dict:
    return {
        "id": e.id,
        "title": e.title,
        "description": e.description,
        "amount": float(e.amount),
        "category": e.category,
        "receipt_url": e.receipt_url,
        "created_by": e.created_by,
        "created_at": e.created_at.isoformat(),
        "approve_count": approve,
        "reject_count": reject,
        "my_vote": my_vote,
    }


@router.get("")
async def list_expenses(
    category: Optional[ExpenseCategory] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expenses, total = await expense_service.list_expenses(
        db, current_user.complex_id, category, skip, limit
    )
    items = []
    for e in expenses:
        approve, reject = await expense_service.get_vote_counts(db, e.id)
        my_vote = await expense_service.get_user_vote(db, e.id, current_user.id)
        items.append(_serialize_expense(e, approve, reject, my_vote))
    return {"data": items, "meta": {"total": total, "skip": skip, "limit": limit}}


@router.post("", status_code=201)
async def create_expense(
    data: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    expense = await expense_service.create_expense(
        db, data, current_user.complex_id, current_user.id
    )
    return {
        "data": {
            "id": expense.id,
            "title": expense.title,
            "amount": float(expense.amount),
            "category": expense.category,
            "created_at": expense.created_at.isoformat(),
        }
    }


@router.get("/{expense_id}")
async def get_expense(
    expense_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = await expense_service.get_expense(db, expense_id, current_user.complex_id)
    approve, reject = await expense_service.get_vote_counts(db, expense.id)
    my_vote = await expense_service.get_user_vote(db, expense.id, current_user.id)
    return {"data": _serialize_expense(expense, approve, reject, my_vote)}


@router.post("/{expense_id}/vote", status_code=201)
async def vote_on_expense(
    expense_id: str,
    data: VoteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vote = await expense_service.cast_vote(
        db, expense_id, current_user.complex_id, current_user.id, data
    )
    return {"data": {"expense_id": expense_id, "value": vote.value}}


@router.delete("/{expense_id}", status_code=204)
async def delete_expense(
    expense_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    await expense_service.delete_expense(db, expense_id, current_user.complex_id)
