import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class IssueStatus(str, PyEnum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    complex_id: Mapped[str] = mapped_column(
        String, ForeignKey("apartment_complexes.id"), nullable=False
    )
    raised_by: Mapped[str] = mapped_column(
        String, ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    status: Mapped[IssueStatus] = mapped_column(
        Enum(IssueStatus), nullable=False, default=IssueStatus.OPEN
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    complex: Mapped["ApartmentComplex"] = relationship(
        "ApartmentComplex", back_populates="issues"
    )
    reporter: Mapped["User"] = relationship("User", foreign_keys=[raised_by])
