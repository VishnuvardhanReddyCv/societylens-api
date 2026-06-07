from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.announcement import AnnouncementCreate
from app.models.user import User
from app.core.dependencies import get_current_user, require_admin
from app.services import announcement_service

router = APIRouter(prefix="/api/announcements", tags=["announcements"])


def _serialize_ann(a) -> dict:
    return {
        "id": a.id,
        "title": a.title,
        "body": a.body,
        "created_by": a.created_by,
        "complex_id": a.complex_id,
        "created_at": a.created_at.isoformat(),
    }


@router.get("")
async def list_announcements(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    anns, total = await announcement_service.list_announcements(
        db, current_user.complex_id, skip, limit
    )
    return {
        "data": [_serialize_ann(a) for a in anns],
        "meta": {"total": total, "skip": skip, "limit": limit},
    }


@router.post("", status_code=201)
async def create_announcement(
    data: AnnouncementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    ann = await announcement_service.create_announcement(
        db, data, current_user.complex_id, current_user.id
    )
    return {"data": _serialize_ann(ann)}


@router.delete("/{announcement_id}", status_code=204)
async def delete_announcement(
    announcement_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    await announcement_service.delete_announcement(
        db, announcement_id, current_user.complex_id
    )
