from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user
from api.dependencies.database import get_async_db
from crud.favorite import crud_favorite
from crud.organisation.organisation import crud_organisation
from models import User
from models.favorite.favorite import Favorite
from schemas.endpoints.paginated_response import (
    OrganisationFavoritePaginatedResponse,
)
from utilities.paginated_response import response_with_pagination

router = APIRouter()


@router.get(
    "/",
    response_model=OrganisationFavoritePaginatedResponse,
    status_code=status.HTTP_200_OK,
)
async def read_favorite_organisations(
    db: AsyncSession = Depends(get_async_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
):
    objects = await crud_favorite.get_organizations_by_user_id_with_count(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return await response_with_pagination(limit=limit, skip=skip, data=objects)


@router.post(
    "/{organisation_id}/",
    status_code=status.HTTP_201_CREATED,
)
async def add_favorite_organisation(
    organisation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    found_organisation = await crud_organisation.get_by_id(
        db=db, obj_id=organisation_id
    )
    if not found_organisation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organisation not found",
        )
    current_user = await db.merge(current_user)
    favorite_ids = {f.organisation_id for f in current_user.favorites}
    if found_organisation.id in favorite_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organisation with ID: {organisation_id}"
            "is already added to favorites",
        )
    try:
        new_favorite = Favorite(
            user_id=current_user.id,
            organisation_id=organisation_id,
        )
        current_user.favorites.append(new_favorite)
        await db.commit()
    except Exception as ex:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
        )


@router.delete(
    "/{organisation_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_favorite_organisation(
    organisation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    found_organisation = await crud_organisation.get_by_id(
        db=db, obj_id=organisation_id
    )
    if not found_organisation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organisation with ID: {organisation_id} not found",
        )
    for favorite in current_user.favorites:
        if favorite.organisation_id == found_organisation.id:
            current_user.favorites.remove(favorite)
            await db.merge(favorite)
            await db.commit()
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Favorite organisation not found in the"
        "current user's favorites",
    )
