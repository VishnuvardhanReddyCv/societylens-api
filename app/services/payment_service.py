from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.payment import Payment, PaymentStatus
from app.models.user import User, UserRole
from app.models.complex import Unit
from app.schemas.payment import PaymentCreate, TenantPaymentSummary


async def list_payments(
    db: AsyncSession,
    complex_id: str,
    status: PaymentStatus | None = None,
    user_id: str | None = None,
    skip: int = 0,
    limit: int = 50,
):
    query = select(Payment).where(Payment.complex_id == complex_id)
    if status:
        query = query.where(Payment.status == status)
    if user_id:
        query = query.where(Payment.user_id == user_id)
    query = query.order_by(Payment.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    payments = result.scalars().all()

    count_query = select(func.count(Payment.id)).where(Payment.complex_id == complex_id)
    if status:
        count_query = count_query.where(Payment.status == status)
    if user_id:
        count_query = count_query.where(Payment.user_id == user_id)
    total = (await db.execute(count_query)).scalar() or 0

    return payments, total


async def create_payment(
    db: AsyncSession,
    data: PaymentCreate,
    complex_id: str,
    current_user: User,
) -> Payment:
    if current_user.role == UserRole.ADMIN:
        # Admin records on behalf of a tenant — must supply user_id, auto-approved
        if not data.user_id:
            raise HTTPException(status_code=400, detail="user_id is required when admin records a payment")
        target_result = await db.execute(
            select(User).where(User.id == data.user_id, User.complex_id == complex_id)
        )
        target = target_result.scalar_one_or_none()
        if not target:
            raise HTTPException(status_code=404, detail="Tenant not found in this complex")

        payment = Payment(
            complex_id=complex_id,
            user_id=data.user_id,
            amount=data.amount,
            description=data.description,
            status=PaymentStatus.APPROVED,
            recorded_by=current_user.id,
            approved_by=current_user.id,
            approved_at=datetime.utcnow(),
        )
    else:
        # Tenant records their own payment — goes to admin for approval
        payment = Payment(
            complex_id=complex_id,
            user_id=current_user.id,
            amount=data.amount,
            description=data.description,
            status=PaymentStatus.PENDING,
            recorded_by=current_user.id,
        )

    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment


async def approve_payment(
    db: AsyncSession, payment_id: str, complex_id: str, admin_user: User
) -> Payment:
    payment = await _get_payment(db, payment_id, complex_id)
    if payment.status != PaymentStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only pending payments can be approved")
    payment.status = PaymentStatus.APPROVED
    payment.approved_by = admin_user.id
    payment.approved_at = datetime.utcnow()
    await db.commit()
    await db.refresh(payment)
    return payment


async def reject_payment(
    db: AsyncSession, payment_id: str, complex_id: str, admin_user: User
) -> Payment:
    payment = await _get_payment(db, payment_id, complex_id)
    if payment.status != PaymentStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only pending payments can be rejected")
    payment.status = PaymentStatus.REJECTED
    payment.approved_by = admin_user.id
    payment.approved_at = datetime.utcnow()
    await db.commit()
    await db.refresh(payment)
    return payment


async def get_tenant_payment_summary(
    db: AsyncSession, complex_id: str
) -> list[TenantPaymentSummary]:
    tenants_result = await db.execute(
        select(User).where(User.complex_id == complex_id, User.role == UserRole.TENANT)
    )
    tenants = tenants_result.scalars().all()

    summary = []
    for tenant in tenants:
        # total approved payments
        total_result = await db.execute(
            select(func.sum(Payment.amount)).where(
                Payment.complex_id == complex_id,
                Payment.user_id == tenant.id,
                Payment.status == PaymentStatus.APPROVED,
            )
        )
        total_paid = float(total_result.scalar() or 0)

        count_result = await db.execute(
            select(func.count(Payment.id)).where(
                Payment.complex_id == complex_id,
                Payment.user_id == tenant.id,
                Payment.status == PaymentStatus.APPROVED,
            )
        )
        payment_count = count_result.scalar() or 0

        last_result = await db.execute(
            select(func.max(Payment.approved_at)).where(
                Payment.complex_id == complex_id,
                Payment.user_id == tenant.id,
                Payment.status == PaymentStatus.APPROVED,
            )
        )
        last_payment_at = last_result.scalar()

        # unit number
        unit_number = None
        if tenant.unit_id:
            unit_result = await db.execute(
                select(Unit).where(Unit.id == tenant.unit_id)
            )
            unit = unit_result.scalar_one_or_none()
            unit_number = unit.unit_number if unit else None

        summary.append(
            TenantPaymentSummary(
                user_id=tenant.id,
                name=tenant.name,
                email=tenant.email,
                unit_number=unit_number,
                total_paid=total_paid,
                payment_count=payment_count,
                last_payment_at=last_payment_at,
            )
        )

    return sorted(summary, key=lambda x: x.total_paid, reverse=True)


async def get_total_collected(db: AsyncSession, complex_id: str) -> float:
    result = await db.execute(
        select(func.sum(Payment.amount)).where(
            Payment.complex_id == complex_id,
            Payment.status == PaymentStatus.APPROVED,
        )
    )
    return float(result.scalar() or 0)


async def _get_payment(db: AsyncSession, payment_id: str, complex_id: str) -> Payment:
    result = await db.execute(
        select(Payment).where(
            Payment.id == payment_id, Payment.complex_id == complex_id
        )
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
