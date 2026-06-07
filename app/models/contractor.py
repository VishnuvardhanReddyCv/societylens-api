import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Contractor(Base):
    """Phase 5: Contractor registry for rating and linking to expenses."""

    __tablename__ = "contractors"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    complex_id: Mapped[str] = mapped_column(
        String, ForeignKey("apartment_complexes.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    reviews: Mapped[list["ContractorReview"]] = relationship(
        "ContractorReview", back_populates="contractor", cascade="all, delete-orphan"
    )


class ContractorReview(Base):
    """Phase 5: Resident ratings for contractors."""

    __tablename__ = "contractor_reviews"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    contractor_id: Mapped[str] = mapped_column(
        String, ForeignKey("contractors.id"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id"), nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    contractor: Mapped["Contractor"] = relationship(
        "Contractor", back_populates="reviews"
    )
    reviewer: Mapped["User"] = relationship("User")
