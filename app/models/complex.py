import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ApartmentComplex(Base):
    __tablename__ = "apartment_complexes"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    invite_code: Mapped[str] = mapped_column(String(6), unique=True, nullable=False)
    # Phase 2: Razorpay subscription status placeholder
    payment_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    units: Mapped[list["Unit"]] = relationship(
        "Unit", back_populates="complex", cascade="all, delete-orphan"
    )
    users: Mapped[list["User"]] = relationship("User", back_populates="complex")
    expenses: Mapped[list["Expense"]] = relationship("Expense", back_populates="complex")
    issues: Mapped[list["Issue"]] = relationship("Issue", back_populates="complex")
    announcements: Mapped[list["Announcement"]] = relationship(
        "Announcement", back_populates="complex"
    )


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    complex_id: Mapped[str] = mapped_column(
        String, ForeignKey("apartment_complexes.id"), nullable=False
    )
    unit_number: Mapped[str] = mapped_column(String(50), nullable=False)
    floor: Mapped[int | None] = mapped_column(Integer, nullable=True)

    complex: Mapped["ApartmentComplex"] = relationship(
        "ApartmentComplex", back_populates="units"
    )
    users: Mapped[list["User"]] = relationship("User", back_populates="unit")
