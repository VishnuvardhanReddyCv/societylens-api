import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import String, DateTime, ForeignKey, Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PaymentStatus(str, PyEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    complex_id: Mapped[str] = mapped_column(
        String, ForeignKey("apartment_complexes.id"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id"), nullable=False
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING
    )
    # who entered this record — tenant entering their own, or admin on behalf
    recorded_by: Mapped[str] = mapped_column(
        String, ForeignKey("users.id"), nullable=False
    )
    approved_by: Mapped[str | None] = mapped_column(
        String, ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    payer: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    recorder: Mapped["User"] = relationship("User", foreign_keys=[recorded_by])
    approver: Mapped["User"] = relationship("User", foreign_keys=[approved_by])
