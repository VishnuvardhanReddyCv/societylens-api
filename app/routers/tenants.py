from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.complex import ApartmentComplex
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/complexes", tags=["complexes"])


@router.get("/me")
async def get_my_complex(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ApartmentComplex).where(ApartmentComplex.id == current_user.complex_id)
    )
    complex_obj = result.scalar_one()
    return {
        "data": {
            "id": complex_obj.id,
            "name": complex_obj.name,
            "address": complex_obj.address,
            "city": complex_obj.city,
            "invite_code": complex_obj.invite_code,
        }
    }
