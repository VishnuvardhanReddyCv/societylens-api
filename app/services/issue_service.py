from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.issue import Issue, IssueStatus
from app.schemas.issue import IssueCreate, IssueUpdate
from app.services.notification_service import notify_issue_status_changed


async def list_issues(
    db: AsyncSession,
    complex_id: str,
    status: IssueStatus | None = None,
    skip: int = 0,
    limit: int = 20,
):
    query = select(Issue).where(Issue.complex_id == complex_id)
    if status:
        query = query.where(Issue.status == status)
    query = query.order_by(Issue.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    issues = result.scalars().all()

    count_query = select(func.count(Issue.id)).where(Issue.complex_id == complex_id)
    if status:
        count_query = count_query.where(Issue.status == status)
    total = (await db.execute(count_query)).scalar() or 0

    return issues, total


async def get_issue(db: AsyncSession, issue_id: str, complex_id: str) -> Issue:
    result = await db.execute(
        select(Issue).where(Issue.id == issue_id, Issue.complex_id == complex_id)
    )
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue


async def create_issue(
    db: AsyncSession,
    data: IssueCreate,
    complex_id: str,
    user_id: str,
) -> Issue:
    issue = Issue(
        complex_id=complex_id,
        raised_by=user_id,
        title=data.title,
        description=data.description,
    )
    db.add(issue)
    await db.commit()
    await db.refresh(issue)
    return issue


async def update_issue_status(
    db: AsyncSession, issue_id: str, complex_id: str, data: IssueUpdate
) -> Issue:
    issue = await get_issue(db, issue_id, complex_id)
    old_status = issue.status
    issue.status = data.status
    await db.commit()
    await db.refresh(issue)
    await notify_issue_status_changed(issue_id, old_status, data.status)
    return issue
