import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import String, DateTime, ForeignKey, Enum, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ExpenseCategory(str, PyEnum):
    MAINTENANCE = "MAINTENANCE"
    REPAIR = "REPAIR"
    UTILITY = "UTILITY"
    SECURITY = "SECURITY"
    AMENITY = "AMENITY"
    OTHER = "OTHER"


class VoteValue(str, PyEnum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    complex_id: Mapped[str] = mapped_column(
        String, ForeignKey("apartment_complexes.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    # Phase 2: Razorpay uses this field — numeric(10,2) not float
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    category: Mapped[ExpenseCategory] = mapped_column(
        Enum(ExpenseCategory), nullable=False
    )
    receipt_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_by: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    # Phase 5: link to contractor who performed the work
    contractor_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("contractors.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    complex: Mapped["ApartmentComplex"] = relationship(
        "ApartmentComplex", back_populates="expenses"
    )
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    votes: Mapped[list["Vote"]] = relationship(
        "Vote", back_populates="expense", cascade="all, delete-orphan"
    )
    contractor: Mapped["Contractor"] = relationship(
        "Contractor", foreign_keys=[contractor_id]
    )


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    expense_id: Mapped[str] = mapped_column(
        String, ForeignKey("expenses.id"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id"), nullable=False
    )
    value: Mapped[VoteValue] = mapped_column(Enum(VoteValue), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    expense: Mapped["Expense"] = relationship("Expense", back_populates="votes")
    user: Mapped["User"] = relationship("User")

    __table_args__ = (
        UniqueConstraint("expense_id", "user_id", name="uq_vote_expense_user"),
    )
