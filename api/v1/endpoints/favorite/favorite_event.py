from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from api.dependencies.auth import get_current_user
from api.dependencies.database import get_async_db
from api.dependencies.ip import get_current_user_ip
from crud.event import crud_event
from crud.favorite import crud_favorite
from models import User
from models.favorite import Favorite
from schemas.endpoints.paginated_response import EventPaginatedResponse
from services.user.language import get_user_language

router = APIRouter()


@router.get(
    "/",
    response_model=EventPaginatedResponse,
    status_code=status.HTTP_200_OK,
)
async def read_favorite_events(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    current_user_ip: Optional[str] = Depends(get_current_user_ip),
) -> EventPaginatedResponse:
    locale = await get_user_language(request=request, db=db, user=current_user)
    return await crud_favorite.get_events_by_user_id_with_count(
        db=db,
        locale=locale,
        user_id=current_user.id,
        current_user_ip=current_user_ip,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/{event_id}/",
    status_code=status.HTTP_201_CREATED,
)
async def add_favorite_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> None:
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
) -> None:
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
