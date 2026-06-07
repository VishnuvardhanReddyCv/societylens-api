from fastapi import APIRouter, Depends

from app.models.user import User
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/contractors", tags=["contractors"])

# TODO Phase 5: Contractor rating system.
# Implement list, create, get, and review endpoints.
# Link contractors to expenses via expense.contractor_id.


@router.get("")
async def list_contractors(current_user: User = Depends(get_current_user)):
    return {"data": [], "meta": {"total": 0, "skip": 0, "limit": 20}}
