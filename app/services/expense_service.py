from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.expense import Expense, Vote, VoteValue
from app.schemas.expense import ExpenseCreate, VoteRequest


async def list_expenses(
    db: AsyncSession,
    complex_id: str,
    category=None,
    skip: int = 0,
    limit: int = 20,
):
    query = select(Expense).where(Expense.complex_id == complex_id)
    if category:
        query = query.where(Expense.category == category)
    query = query.order_by(Expense.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    expenses = result.scalars().all()

    count_query = select(func.count(Expense.id)).where(Expense.complex_id == complex_id)
    if category:
        count_query = count_query.where(Expense.category == category)
    total = (await db.execute(count_query)).scalar() or 0

    return expenses, total


async def get_expense(db: AsyncSession, expense_id: str, complex_id: str) -> Expense:
    result = await db.execute(
        select(Expense).where(
            Expense.id == expense_id, Expense.complex_id == complex_id
        )
    )
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


async def create_expense(
    db: AsyncSession,
    data: ExpenseCreate,
    complex_id: str,
    user_id: str,
) -> Expense:
    expense = Expense(
        complex_id=complex_id,
        title=data.title,
        description=data.description,
        amount=data.amount,
        category=data.category,
        receipt_url=data.receipt_url,
        created_by=user_id,
    )
    db.add(expense)
    await db.commit()
    await db.refresh(expense)
    return expense


async def delete_expense(db: AsyncSession, expense_id: str, complex_id: str) -> None:
    expense = await get_expense(db, expense_id, complex_id)
    await db.delete(expense)
    await db.commit()


async def cast_vote(
    db: AsyncSession,
    expense_id: str,
    complex_id: str,
    user_id: str,
    data: VoteRequest,
) -> Vote:
    await get_expense(db, expense_id, complex_id)

    result = await db.execute(
        select(Vote).where(Vote.expense_id == expense_id, Vote.user_id == user_id)
    )
    vote = result.scalar_one_or_none()

    if vote:
        vote.value = data.value
    else:
        vote = Vote(expense_id=expense_id, user_id=user_id, value=data.value)
        db.add(vote)

    await db.commit()
    await db.refresh(vote)
    return vote


async def get_vote_counts(db: AsyncSession, expense_id: str) -> tuple[int, int]:
    approve = (
        await db.execute(
            select(func.count(Vote.id)).where(
                Vote.expense_id == expense_id, Vote.value == VoteValue.APPROVE
            )
        )
    ).scalar() or 0
    reject = (
        await db.execute(
            select(func.count(Vote.id)).where(
                Vote.expense_id == expense_id, Vote.value == VoteValue.REJECT
            )
        )
    ).scalar() or 0
    return approve, reject


async def get_user_vote(
    db: AsyncSession, expense_id: str, user_id: str
) -> str | None:
    result = await db.execute(
        select(Vote).where(Vote.expense_id == expense_id, Vote.user_id == user_id)
    )
    vote = result.scalar_one_or_none()
    return vote.value if vote else None
