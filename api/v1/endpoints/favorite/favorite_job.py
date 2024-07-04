from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user
from api.dependencies.database import get_async_db
from api.dependencies.ip import get_current_user_ip
from crud.favorite import crud_favorite
from crud.frilance.job import crud_job
from models import User
from models.favorite import Favorite
from schemas.endpoints.paginated_response import JobPaginatedResponse

router = APIRouter()


@router.get(
    "/",
    response_model=JobPaginatedResponse,
    status_code=status.HTTP_200_OK,
)
async def read_favorite_jobs(
    db: AsyncSession = Depends(get_async_db),
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    current_user_ip: Optional[str] = Depends(get_current_user_ip),
):
    return await crud_favorite.get_jobs_by_user_id_with_count(
        db=db,
        user_id=current_user.id,
        current_user_ip=current_user_ip,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/{job_id}/",
    status_code=status.HTTP_201_CREATED,
)
async def add_favorite_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    found_job = await crud_job.get_by_id(
        db=db,
        obj_id=job_id,
    )
    if not found_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID: {job_id} not found",
        )
    current_user = await db.merge(current_user)
    favorite_ids = {favorite.job_id for favorite in current_user.favorites}
    if found_job.id in favorite_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job with ID: {job_id} " "is already added to favorites",
        )
    new_favorite = Favorite(
        user_id=current_user.id,
        job_id=job_id,
    )
    current_user.favorites.append(new_favorite)
    await db.commit()


@router.delete(
    "/{job_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_favorite_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    found_job = await crud_job.get_by_id(db=db, obj_id=job_id)
    if not found_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID: {job_id} not found",
        )
    for favorite in current_user.favorites:
        if favorite.job_id == found_job.id:
            current_user.favorites.remove(favorite)
            await db.merge(favorite)
            await db.commit()
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Favorite job with ID: {job_id} not found in the"
        "current user's favorites",
    )
