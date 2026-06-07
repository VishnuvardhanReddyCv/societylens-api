import random
import string

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.complex import ApartmentComplex, Unit
from app.models.user import User, UserRole
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.user import RegisterRequest, JoinRequest, LoginRequest


def _generate_invite_code() -> str:
    return "".join(random.choices(string.digits, k=6))


async def register_complex(db: AsyncSession, data: RegisterRequest):
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    invite_code = _generate_invite_code()
    while True:
        existing = await db.execute(
            select(ApartmentComplex).where(ApartmentComplex.invite_code == invite_code)
        )
        if not existing.scalar_one_or_none():
            break
        invite_code = _generate_invite_code()

    complex_obj = ApartmentComplex(
        name=data.complex_name,
        address=data.address,
        city=data.city,
        invite_code=invite_code,
    )
    db.add(complex_obj)
    await db.flush()

    user = User(
        complex_id=complex_obj.id,
        name=data.name,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role=UserRole.ADMIN,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(
        {
            "sub": user.id,
            "complex_id": user.complex_id,
            "role": user.role,
            "email": user.email,
        }
    )
    return token, user


async def join_complex(db: AsyncSession, data: JoinRequest):
    result = await db.execute(
        select(ApartmentComplex).where(ApartmentComplex.invite_code == data.invite_code)
    )
    complex_obj = result.scalar_one_or_none()
    if not complex_obj:
        raise HTTPException(status_code=404, detail="Invalid invite code")

    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    unit = Unit(complex_id=complex_obj.id, unit_number=data.unit_number)
    db.add(unit)
    await db.flush()

    user = User(
        complex_id=complex_obj.id,
        unit_id=unit.id,
        name=data.name,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role=UserRole.TENANT,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(
        {
            "sub": user.id,
            "complex_id": user.complex_id,
            "role": user.role,
            "email": user.email,
        }
    )
    return token, user


async def login(db: AsyncSession, data: LoginRequest):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(
        {
            "sub": user.id,
            "complex_id": user.complex_id,
            "role": user.role,
            "email": user.email,
        }
    )
    return token, user
