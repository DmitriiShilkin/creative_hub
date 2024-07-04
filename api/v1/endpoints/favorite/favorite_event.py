from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user
from api.dependencies.database import get_async_db
from crud.event import crud_event
from crud.favorite import crud_favorite
from models import User
from models.favorite import Favorite
from schemas.event import EventSimpleResponse

router = APIRouter()


@router.get(
    "/",
    response_model=list[EventSimpleResponse],
    status_code=status.HTTP_200_OK,
)
async def read_favorite_events(
    db: AsyncSession = Depends(get_async_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
):
    return await crud_favorite.get_events_by_user_id(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )


@router.post(
    "/{event_id}/",
    status_code=status.HTTP_201_CREATED,
)
async def add_favorite_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    found_event = await crud_event.get_by_id_extended(db=db, obj_id=event_id)
    if not found_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    current_user = await db.merge(current_user)
    favorite_ids = {f.event_id for f in current_user.favorites}
    if found_event.id in favorite_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Event with ID: {event_id}"
            "is already added to favorites",
        )
    new_favorite = Favorite(
        user_id=current_user.id,
        event_id=event_id,
    )
    current_user.favorites.append(new_favorite)
    await db.commit()


@router.delete(
    "/{event_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_favorite_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    found_event = await crud_event.get_by_id_extended(db=db, obj_id=event_id)
    if not found_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID: {event_id} not found",
        )
    for favorite in current_user.favorites:
        if favorite.event_id == found_event.id:
            current_user.favorites.remove(favorite)
            await db.merge(favorite)
            await db.commit()
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Favorite organisation not found in the"
        "current user's favorites",
    )
