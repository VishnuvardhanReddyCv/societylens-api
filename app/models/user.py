import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, PyEnum):
    ADMIN = "ADMIN"
    TENANT = "TENANT"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    complex_id: Mapped[str] = mapped_column(
        String, ForeignKey("apartment_complexes.id"), nullable=False
    )
    unit_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("units.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), nullable=False, default=UserRole.TENANT
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    complex: Mapped["ApartmentComplex"] = relationship(
        "ApartmentComplex", back_populates="users"
    )
    unit: Mapped["Unit"] = relationship("Unit", back_populates="users")
    device_tokens: Mapped[list["DeviceToken"]] = relationship(
        "DeviceToken", back_populates="user", cascade="all, delete-orphan"
    )
