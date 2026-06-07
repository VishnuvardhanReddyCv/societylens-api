from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.schemas.payment import PaymentCreate
from app.models.payment import PaymentStatus
from app.models.user import User
from app.models.complex import Unit
from app.core.dependencies import get_current_user, require_admin
from app.services import payment_service

router = APIRouter(prefix="/api/payments", tags=["payments"])


async def _enrich(payment, db: AsyncSession) -> dict:
    """Attach payer name and unit to a payment dict."""
    payer_result = await db.execute(select(User).where(User.id == payment.user_id))
    payer = payer_result.scalar_one_or_none()
    unit_number = None
    if payer and payer.unit_id:
        unit_result = await db.execute(select(Unit).where(Unit.id == payer.unit_id))
        unit = unit_result.scalar_one_or_none()
        unit_number = unit.unit_number if unit else None
    return {
        "id": payment.id,
        "complex_id": payment.complex_id,
        "user_id": payment.user_id,
        "amount": float(payment.amount),
        "description": payment.description,
        "status": payment.status,
        "recorded_by": payment.recorded_by,
        "approved_by": payment.approved_by,
        "created_at": payment.created_at.isoformat(),
        "approved_at": payment.approved_at.isoformat() if payment.approved_at else None,
        "payer_name": payer.name if payer else None,
        "payer_unit": unit_number,
    }


@router.get("")
async def list_payments(
    status: Optional[PaymentStatus] = None,
    user_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payments, total = await payment_service.list_payments(
        db, current_user.complex_id, status, user_id, skip, limit
    )
    items = [await _enrich(p, db) for p in payments]
    return {"data": items, "meta": {"total": total, "skip": skip, "limit": limit}}


@router.get("/summary")
async def tenant_payment_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    summary = await payment_service.get_tenant_payment_summary(db, current_user.complex_id)
    return {"data": [s.model_dump() for s in summary]}


@router.post("", status_code=201)
async def create_payment(
    data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = await payment_service.create_payment(db, data, current_user.complex_id, current_user)
    return {"data": await _enrich(payment, db)}


@router.patch("/{payment_id}/approve")
async def approve_payment(
    payment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    payment = await payment_service.approve_payment(db, payment_id, current_user.complex_id, current_user)
    return {"data": await _enrich(payment, db)}


@router.patch("/{payment_id}/reject")
async def reject_payment(
    payment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    payment = await payment_service.reject_payment(db, payment_id, current_user.complex_id, current_user)
    return {"data": await _enrich(payment, db)}
