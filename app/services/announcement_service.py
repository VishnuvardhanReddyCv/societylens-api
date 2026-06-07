from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.announcement import Announcement
from app.schemas.announcement import AnnouncementCreate
from app.services.notification_service import notify_new_announcement


async def list_announcements(
    db: AsyncSession, complex_id: str, skip: int = 0, limit: int = 20
):
    query = (
        select(Announcement)
        .where(Announcement.complex_id == complex_id)
        .order_by(Announcement.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    announcements = result.scalars().all()

    total = (
        await db.execute(
            select(func.count(Announcement.id)).where(
                Announcement.complex_id == complex_id
            )
        )
    ).scalar() or 0

    return announcements, total


async def create_announcement(
    db: AsyncSession,
    data: AnnouncementCreate,
    complex_id: str,
    user_id: str,
) -> Announcement:
    announcement = Announcement(
        complex_id=complex_id,
        title=data.title,
        body=data.body,
        created_by=user_id,
    )
    db.add(announcement)
    await db.commit()
    await db.refresh(announcement)
    await notify_new_announcement(announcement.id, complex_id)
    return announcement


async def delete_announcement(
    db: AsyncSession, announcement_id: str, complex_id: str
) -> None:
    result = await db.execute(
        select(Announcement).where(
            Announcement.id == announcement_id,
            Announcement.complex_id == complex_id,
        )
    )
    ann = result.scalar_one_or_none()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    await db.delete(ann)
    await db.commit()
