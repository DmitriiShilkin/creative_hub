from datetime import datetime, UTC
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi_filter import FilterDepends
from pydantic import ValidationError
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from api.dependencies.auth import get_current_user, get_current_user_optional
from api.dependencies.database import get_async_db
from api.dependencies.ip import get_current_user_ip
from api.dependencies.redis import get_redis
from api.filters.event import (
    AuthorEventFilters,
    EventFilters,
)
from constants.event import EventType
from constants.i18n import EventLanguage
from crud.event import crud_event
from crud.event_participants import crud_event_participants
from crud.event_with_counters import crud_ewc
from crud.status import crud_status
from crud.user import crud_user
from databases.database import get_async_session
from models import User, EventParticipants
from schemas.endpoints.paginated_response import (
    EventPaginatedResponse,
)
from schemas.event import (
    EventCreateDraft,
    EventLanguagesResponse,
    EventResponse,
    EventTypesResponse,
    EventUpdate,
    EventWithCountersResponse,
    EventCountResponse,
)
from schemas.user.contact_person import ContactPersonAddCreateMulty
from services.event import event, event_read
from services.redis import add_to_redis_browsing_now, get_browsing_now_by_id
from services.user.language import get_user_language
from utilities.exception import (
    SomeObjectsNotFoundError,
    OperationConstraintError,
)

router = APIRouter()


@router.get("/", response_model=EventPaginatedResponse)
async def read_events(
    request: Request,
    filters: EventFilters = FilterDepends(EventFilters),
    db: AsyncSession = Depends(get_async_session),
    limit: int = 20,
    skip: int = 0,
    current_user: Optional[User] = Depends(get_current_user_optional),
    current_user_ip: Optional[str] = Depends(get_current_user_ip),
    redis: Redis = Depends(get_redis),
    favorite: bool = False,
):
    if favorite and not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required to access favorites",
        )
    locale = await get_user_language(request=request, db=db, user=current_user)
    current_user_id = current_user.id if current_user else None
    return await event_read.read_events(
        db=db,
        redis=redis,
        limit=limit,
        skip=skip,
        current_user_id=current_user_id,
        current_user_ip=current_user_ip,
        filters=filters,
        favorite=favorite,
        locale=locale,
    )


@router.get("/author/all/", response_model=EventPaginatedResponse)
async def read_events_for_author(
    request: Request,
    filters: AuthorEventFilters = FilterDepends(AuthorEventFilters),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    skip: int = 0,
    redis: Redis = Depends(get_redis),
):
    locale = await get_user_language(request=request, db=db, user=current_user)
    return await event_read.read_events_for_author(
        db=db,
        filters=filters,
        redis=redis,
        limit=limit,
        skip=skip,
        author_id=current_user.id,
        locale=locale,
    )


@router.get("/author/{author_uid}/", response_model=EventPaginatedResponse)
async def read_events_by_author(
    request: Request,
    author_uid: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: Optional[User] = Depends(get_current_user_optional),
    current_user_ip: Optional[str] = Depends(get_current_user_ip),
    limit: int = 20,
    skip: int = 0,
    redis: Redis = Depends(get_redis),
):
    found_user = await crud_user.get_by_uid_fast(db=db, uid=author_uid)
    if not found_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with uuid {author_uid} not found",
        )
    locale = await get_user_language(request=request, db=db, user=current_user)
    current_user_id = current_user.id if current_user else None
    return await event_read.read_events_by_author(
        db=db,
        redis=redis,
        limit=limit,
        author_id=found_user.id,
        skip=skip,
        current_user_id=current_user_id,
        current_user_ip=current_user_ip,
        locale=locale,
    )


@router.get("/{event_id}/", response_model=EventWithCountersResponse)
async def read_event(
    event_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
    current_user_ip: Optional[str] = Depends(get_current_user_ip),
    redis: Redis = Depends(get_redis),
):
    author_id = current_user.id if current_user is not None else None
    found_event = await crud_ewc.get_by_id(
        db=db,
        obj_id=event_id,
        author_id=author_id,
        current_user_ip=current_user_ip,
    )
    if not found_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    await add_to_redis_browsing_now(
        redis=redis,
        event_id=found_event.Event.id,
        user_id=current_user.id if current_user else current_user_ip,
    )
    new_participants_count = await event_read.create_update_event_view(
        db=db,
        event=found_event.Event,
        participants_count=found_event.participants_count,
        current_user_id=current_user.id if current_user else None,
        current_user_ip=current_user_ip,
    )
    await db.commit()
    browsing_now = await get_browsing_now_by_id(
        redis=redis, event_id=found_event.Event.id
    )
    return EventWithCountersResponse.model_validate(
        obj=found_event.Event,
        from_attributes=True,
        context={
            "new_participants_count": new_participants_count,
            "participants_count": found_event.participants_count,
            "views": found_event.views,
            "browsing_now": browsing_now,
            "is_favorite": found_event.is_favorite,
        },
    )


@router.get(
    "/author/all/count/",
    response_model=EventCountResponse,
    status_code=status.HTTP_200_OK,
)
async def read_events_counts_for_author(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    return await crud_ewc.get_events_count_for_author(
        db=db, author_id=current_user.id
    )


@router.post("/views/")
async def view_events(
    events_ids: list[int],
    db: AsyncSession = Depends(get_async_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
    current_user_ip: Optional[str] = Depends(get_current_user_ip),
):
    current_user_id = current_user.id if current_user else None
    try:
        await event_read.create_update_event_view_multi(
            db,
            events_ids=events_ids,
            current_user_id=current_user_id,
            current_user_ip=current_user_ip,
        )
    except SomeObjectsNotFoundError as ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ex.message
        ) from ex


@router.post(
    "/",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    description="""
       **Required fields when `is_draft=True`:** `title`,
       `is_free`, `is_online`.

       \n**Required fields when `is_draft=False`:** `title`,
       `organizers_uids`, `is_free`, `is_online`, `timezone_id`,
       `event_type`, `language`, `start_datetime`, `end_datetime`.
       """,
)
async def create_event(
    create_data: EventCreateDraft,
    contact_person_data: ContactPersonAddCreateMulty,
    photo: Optional[UploadFile] = None,
    event_cover: Optional[UploadFile] = None,
    contact_person_files: List[UploadFile] = [],  # noqa: B006
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await event.create(
            db=db,
            create_data=create_data,
            user_id=current_user.id,
            photo=photo,
            event_cover=event_cover,
            contact_person_data=contact_person_data,
            contact_person_files=contact_person_files,
        )
    except SomeObjectsNotFoundError as ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ex.message
        ) from ex
    except ValidationError as ex:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(ex.errors())
        ) from ex


@router.patch("/{event_id}/", response_model=EventResponse)
async def update_event(
    event_id: int,
    update_data: EventUpdate,
    contact_person_data: ContactPersonAddCreateMulty,
    photo: Optional[UploadFile] = None,
    event_cover: Optional[UploadFile] = None,
    contact_person_files: list[UploadFile] = [],  # noqa: B006
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_event = await crud_event.get_by_id_extended(
        db=db, obj_id=event_id, author_id=current_user.id
    )
    if not found_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    if found_event.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission!",
        )
    try:
        return await event.update(
            db=db,
            event=found_event,
            update_data=update_data,
            photo=photo,
            event_cover=event_cover,
            contact_person_data=contact_person_data,
            contact_person_files=contact_person_files,
            user_id=current_user.id,
        )
    except SomeObjectsNotFoundError as ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ex.message
        ) from ex
    except ValidationError as ex:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(ex.errors())
        ) from ex
    except OperationConstraintError as ex:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(ex)
        ) from ex


@router.delete("/{event_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    found_event = await crud_event.get_by_id(db=db, obj_id=event_id)
    if not found_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    if found_event.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission!",
        )
    await crud_event.remove(db=db, obj_id=event_id)


@router.post("/{event_id}/attend/", status_code=status.HTTP_200_OK)
async def attend_event(
    event_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_event = await crud_event.get_by_id_extended(db=db, obj_id=event_id)
    if not found_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    current_user = await db.merge(current_user)
    if current_user.id in {user.user_id for user in found_event.participants}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already registered for this event.",
        )
    found_status = await crud_status.get_new_status_id(db)
    participant = EventParticipants(
        event_id=found_event.id,
        user_id=current_user.id,
        status_id=found_status,
    )
    found_event.participants.append(participant)
    await db.commit()


@router.delete(
    "/{event_id}/cancel_attendance/", status_code=status.HTTP_200_OK
)
async def cancel_attendance(
    event_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_event = await crud_event.get_by_id_extended(db=db, obj_id=event_id)
    if not found_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    found_attendance = await crud_event_participants.get_by_event_and_user_ids(
        db=db, event_id=event_id, user_id=current_user.id
    )
    if not found_attendance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not registered for this event.",
        )
    await db.delete(found_attendance)
    await db.commit()


@router.get("/types/all/", response_model=EventTypesResponse)
async def get_event_types():
    return {"types": [event_type.value for event_type in EventType]}


@router.get("/languages/all/", response_model=EventLanguagesResponse)
async def get_event_languages():
    return {
        "languages": [event_language.value for event_language in EventLanguage]
    }


@router.patch(
    "/publish/{event_id}/",
    status_code=status.HTTP_200_OK,
)
async def publish_event(
    event_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_event = await crud_event.get_by_id(db, obj_id=event_id)
    if not found_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The event not found.",
        )
    if found_event.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the event creator can publish.",
        )
    if found_event.is_draft:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You cannot publish a draft event.",
        )
    if not found_event.is_archived:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The event is already published.",
        )
    found_event.is_archived = False
    found_event.published_at = datetime.now(tz=UTC)
    await db.commit()


@router.patch(
    "/unpublish/{event_id}/",
    status_code=status.HTTP_200_OK,
)
async def unpublish_event(
    event_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_event = await crud_event.get_by_id(db, obj_id=event_id)
    if not found_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The event not found",
        )
    if found_event.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the event creator can unpublish.",
        )
    if found_event.is_archived:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The event is not published.",
        )
    found_event.is_archived = True
    await db.commit()
