from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user
from api.dependencies.database import get_async_db
from crud.user_profile_completeness import crud_profile_completeness
from models import User
from schemas.user.profile_completeness import (
    ProfileCompletenessResponse,
    ProfileCompletenessUpdate,
)

router = APIRouter()


@router.get("/", response_model=ProfileCompletenessResponse)
async def read_user_profile_completeness(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    return await crud_profile_completeness.get_by_id(
        db, obj_id=current_user.profile_completeness.id
    )


@router.patch("/", response_model=ProfileCompletenessResponse)
async def update_user_profile_completeness(
    update_data: ProfileCompletenessUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_profile = await crud_profile_completeness.get_by_id(
        db, obj_id=current_user.profile_completeness.id
    )
    await crud_profile_completeness.update(
        db=db,
        db_obj=found_profile,
        update_data=update_data,
    )
    await db.refresh(found_profile)
    return found_profile
