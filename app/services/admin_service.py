from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.expense import Expense
from app.models.issue import Issue, IssueStatus
from app.models.user import User, UserRole
from app.services.payment_service import get_total_collected


async def get_summary(db: AsyncSession, complex_id: str) -> dict:
    total_result = await db.execute(
        select(func.sum(Expense.amount)).where(Expense.complex_id == complex_id)
    )
    total_spent = total_result.scalar() or Decimal("0")

    open_issues = (
        await db.execute(
            select(func.count(Issue.id)).where(
                Issue.complex_id == complex_id,
                Issue.status == IssueStatus.OPEN,
            )
        )
    ).scalar() or 0

    category_rows = (
        await db.execute(
            select(Expense.category, func.sum(Expense.amount))
            .where(Expense.complex_id == complex_id)
            .group_by(Expense.category)
        )
    ).all()
    spend_by_category = {row[0]: float(row[1]) for row in category_rows}

    total_collected = await get_total_collected(db, complex_id)

    return {
        "total_collected": total_collected,
        "total_spent": float(total_spent),
        "balance": total_collected - float(total_spent),
        "open_issues_count": open_issues,
        "spend_by_category": spend_by_category,
    }


async def list_tenants(
    db: AsyncSession, complex_id: str, skip: int = 0, limit: int = 50
):
    query = (
        select(User)
        .where(User.complex_id == complex_id, User.role == UserRole.TENANT)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    tenants = result.scalars().all()

    total = (
        await db.execute(
            select(func.count(User.id)).where(
                User.complex_id == complex_id, User.role == UserRole.TENANT
            )
        )
    ).scalar() or 0

    return tenants, total
