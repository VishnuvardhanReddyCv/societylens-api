import random
import string

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.schemas.complex import ComplexUpdate
from app.models.complex import ApartmentComplex, Unit
from app.models.user import User
from app.core.dependencies import require_admin
from app.services import admin_service

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/summary")
async def get_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    summary = await admin_service.get_summary(db, current_user.complex_id)
    return {"data": summary}


@router.get("/tenants")
async def list_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    tenants, total = await admin_service.list_tenants(
        db, current_user.complex_id, skip, limit
    )
    items = []
    for t in tenants:
        unit_number = None
        if t.unit_id:
            unit_result = await db.execute(select(Unit).where(Unit.id == t.unit_id))
            unit = unit_result.scalar_one_or_none()
            unit_number = unit.unit_number if unit else None
        items.append({
            "id": t.id,
            "name": t.name,
            "email": t.email,
            "unit_number": unit_number,
            "created_at": t.created_at.isoformat(),
        })
    return {"data": items, "meta": {"total": total, "skip": skip, "limit": limit}}


@router.patch("/invite")
async def regenerate_invite(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    new_code = "".join(random.choices(string.digits, k=6))
    result = await db.execute(
        select(ApartmentComplex).where(ApartmentComplex.id == current_user.complex_id)
    )
    complex_obj = result.scalar_one()
    complex_obj.invite_code = new_code
    await db.commit()
    return {"data": {"invite_code": new_code}}


@router.patch("/settings")
async def update_settings(
    data: ComplexUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(
        select(ApartmentComplex).where(ApartmentComplex.id == current_user.complex_id)
    )
    complex_obj = result.scalar_one()
    if data.name is not None:
        complex_obj.name = data.name
    if data.address is not None:
        complex_obj.address = data.address
    if data.city is not None:
        complex_obj.city = data.city
    await db.commit()
    await db.refresh(complex_obj)
    return {
        "data": {
            "id": complex_obj.id,
            "name": complex_obj.name,
            "address": complex_obj.address,
            "city": complex_obj.city,
        }
    }
