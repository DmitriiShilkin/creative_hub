from typing import List, Optional, Union

from redis import Redis
from redis.asyncio import RedisError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.filters.event import EventFilters
from configs.loggers import logger
from constants.i18n import Languages
from crud.event_view import crud_event_view
from crud.event_with_counters import crud_ewc
from models import Event
from schemas.endpoints.paginated_response import EventPaginatedResponse
from schemas.event_view import EventView
from services.redis import get_browsing_now_by_id
from utilities.queryset import check_found


async def create_update_event_view_multi(
    db: AsyncSession,
    events_ids: List[int],
    current_user_id: Optional[int],
    current_user_ip: Optional[str],
):
    found_events = await crud_ewc.get_multi_by_ids(
        db=db,
        ids=events_ids,
        current_user_id=current_user_id,
        current_user_ip=current_user_ip,
    )
    await check_found(objects=found_events, objects_ids=events_ids)
    for event in found_events:
        await create_update_event_view(
            db=db,
            event=event.Event,
            participants_count=event.participants_count,
            current_user_id=current_user_id,
            current_user_ip=current_user_ip,
        )
    await db.commit()


async def create_update_event_view(
    db: AsyncSession,
    event: Event,
    participants_count: int,
    current_user_id: Optional[int],
    current_user_ip: Optional[str],
) -> int:
    new_participants_count = 0
    if (
        current_user_id is not None or current_user_ip is not None
    ) and not event.event_views:
        try:
            await crud_event_view.create(
                db,
                create_schema=EventView(
                    event_id=event.id,
                    participants_views=participants_count,
                    user_id=current_user_id,
                    ip_address=current_user_ip
                    if not current_user_id
                    else None,
                ),
                commit=False,
            )
        except IntegrityError as ex:
            logger.exception(ex)

    elif (
        event.event_views
        and event.event_views[0].participants_views != participants_count
    ):
        new_participants_count = (
            participants_count - event.event_views[0].participants_views
        )
        event.event_views[0].participants_views = participants_count
    return new_participants_count


async def read_events(
    db: AsyncSession,
    redis: Redis,
    limit: int,
    skip: int,
    current_user_id: Optional[int],
    current_user_ip: Optional[str],
    locale: Languages,
    filters: EventFilters,
    favorite: bool,
) -> EventPaginatedResponse:
    events = await crud_ewc.get_multi(
        db,
        limit=limit,
        locale=locale,
        skip=skip,
        current_user_id=current_user_id,
        current_user_ip=current_user_ip,
        filters=filters,
        favorite=favorite,
    )
    events = EventPaginatedResponse.model_validate(
        events, from_attributes=True
    )
    return await _add_browsing_now(events=events, redis=redis)


async def read_events_by_author(
    db: AsyncSession,
    redis: Redis,
    limit: int,
    skip: int,
    author_id: int,
    current_user_id: Optional[int],
    current_user_ip: Optional[str],
    locale: Languages,
    filters: EventFilters,
    favorite: bool,
) -> EventPaginatedResponse:
    events = await crud_ewc.get_multi(
        db,
        limit=limit,
        locale=locale,
        skip=skip,
        current_user_id=current_user_id,
        current_user_ip=current_user_ip,
        filters=filters,
        favorite=favorite,
        author_id=author_id,
    )
    events = EventPaginatedResponse.model_validate(
        events, from_attributes=True
    )
    return await _add_browsing_now(events=events, redis=redis)


async def read_events_for_author(
    db: AsyncSession,
    redis: Redis,
    limit: int,
    skip: int,
    author_id: int,
    locale: Languages,
    filters: EventFilters,
) -> EventPaginatedResponse:
    events = await crud_ewc.get_multi_for_author(
        db,
        limit=limit,
        locale=locale,
        skip=skip,
        filters=filters,
        author_id=author_id,
    )
    events = EventPaginatedResponse.model_validate(
        events, from_attributes=True
    )
    return await _add_browsing_now(events=events, redis=redis)


async def _add_browsing_now(
    events: Union[EventPaginatedResponse],
    redis: Redis,
) -> Union[EventPaginatedResponse]:
    for event in events.objects:
        try:
            count = await get_browsing_now_by_id(
                redis=redis, event_id=event.id
            )
            event.browsing_now = count
        except RedisError as ex:
            logger.error(ex)
    return events
