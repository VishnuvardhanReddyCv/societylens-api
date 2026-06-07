from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.issue import IssueCreate, IssueUpdate
from app.models.issue import IssueStatus
from app.models.user import User
from app.core.dependencies import get_current_user, require_admin
from app.services import issue_service

router = APIRouter(prefix="/api/issues", tags=["issues"])


def _serialize_issue(i) -> dict:
    return {
        "id": i.id,
        "title": i.title,
        "description": i.description,
        "status": i.status,
        "raised_by": i.raised_by,
        "complex_id": i.complex_id,
        "created_at": i.created_at.isoformat(),
        "updated_at": i.updated_at.isoformat(),
    }


@router.get("")
async def list_issues(
    status: Optional[IssueStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issues, total = await issue_service.list_issues(
        db, current_user.complex_id, status, skip, limit
    )
    return {
        "data": [_serialize_issue(i) for i in issues],
        "meta": {"total": total, "skip": skip, "limit": limit},
    }


@router.post("", status_code=201)
async def create_issue(
    data: IssueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = await issue_service.create_issue(
        db, data, current_user.complex_id, current_user.id
    )
    return {"data": _serialize_issue(issue)}


@router.get("/{issue_id}")
async def get_issue(
    issue_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = await issue_service.get_issue(db, issue_id, current_user.complex_id)
    return {"data": _serialize_issue(issue)}


@router.patch("/{issue_id}")
async def update_issue(
    issue_id: str,
    data: IssueUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    issue = await issue_service.update_issue_status(
        db, issue_id, current_user.complex_id, data
    )
    return {"data": _serialize_issue(issue)}
