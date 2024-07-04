from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user
from api.dependencies.database import get_async_db
from crud.favorite import crud_favorite
from crud.user import crud_user
from models import User
from models.favorite.favorite import Favorite
from schemas.endpoints.paginated_response import UserPaginatedResponse
from utilities.paginated_response import response_with_pagination

router = APIRouter()


@router.get(
    "/",
    response_model=UserPaginatedResponse,
    status_code=status.HTTP_200_OK,
)
async def read_favorite_users(
    db: AsyncSession = Depends(get_async_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
):
    objects = await crud_favorite.get_favorite_users_by_user_id_with_count(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return await response_with_pagination(limit=limit, skip=skip, data=objects)


@router.post(
    "/{user_uid}/",
    status_code=status.HTTP_201_CREATED,
)
async def add_favorite_user(
    user_uid: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    found_user = await crud_user.get_by_uid(db=db, uid=user_uid)

    if not found_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with uid {user_uid} not found",
        )

    if current_user.id == found_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't add yourself to favorite.",
        )
    current_user = await db.merge(current_user)
    favorite_ids = {user.favorite_user_id for user in current_user.favorites}
    if found_user.id in favorite_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with uid {user_uid} is already added to favorites",
        )
    try:
        new_favorite = Favorite(
            user_id=current_user.id,
            favorite_user_id=found_user.id,
        )
        current_user.favorites.append(new_favorite)

        await db.commit()
    except Exception as ex:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
        )


@router.delete(
    "/{user_uid}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_favorite_user(
    user_uid: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    found_user = await crud_user.get_by_uid(db=db, uid=user_uid)
    if not found_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with uid {user_uid} not found",
        )

    for favorite in current_user.favorites:
        if favorite.favorite_user_id == found_user.id:
            current_user.favorites.remove(favorite)
            await db.merge(favorite)
            await db.commit()
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Favorite user not found in the current user's favorites",
    )
