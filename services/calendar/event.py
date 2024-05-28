from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from constants.calendar.period import CalendarEventPeriod
from crud.calendar.event import calendar_event_crud
from models.calendar import CalendarEvent
from schemas.calendar.event import (
    CalendarEventCreate,
    CalendarEventCreateDB,
    CalendarEventUpdate,
)
from utilities.validators.calendar_event import (
    check_participants,
    validate_times,
)


async def get_events_by_period(
    db: AsyncSession, user_id: int, period: CalendarEventPeriod
) -> List[CalendarEvent]:
    if period == CalendarEventPeriod.DAY:
        return await calendar_event_crud.get_today_events_by_user_id(
            db=db, user_id=user_id
        )
    elif period == CalendarEventPeriod.WEEK:
        return await calendar_event_crud.get_week_events_by_user_id(
            db=db, user_id=user_id
        )
    elif period == CalendarEventPeriod.MONTH:
        return await calendar_event_crud.get_month_events_by_user_id(
            db=db, user_id=user_id
        )
    elif period == CalendarEventPeriod.SCHEDULE:
        return await calendar_event_crud.get_all_events_by_user_id(
            db=db, user_id=user_id
        )
    return []


async def create_event(
    db: AsyncSession, create_data: CalendarEventCreate, user_id: int
) -> CalendarEvent:
    create_schema = CalendarEventCreateDB(
        **create_data.model_dump(exclude_unset=True),
        organizer_id=user_id,
    )
    try:
        await validate_times(data=create_data)
        event = await calendar_event_crud.create(
            db=db, create_schema=create_schema, commit=False
        )
        if create_data.participants:
            event.participants = await check_participants(
                db=db, user_id=user_id, participants=create_data.participants
            )
        await db.commit()
        return event
    except ValueError as ex:
        await db.rollback()
        raise ex


async def update_event(
    db: AsyncSession, event: CalendarEvent, update_data: CalendarEventUpdate
) -> CalendarEvent:
    try:
        await validate_times(data=update_data, event=event)
        event.participants = []
        event.participants = await check_participants(
            db=db,
            user_id=event.organizer_id,
            participants=update_data.participants,
        )
        del update_data.participants
        await calendar_event_crud.update(
            db=db, db_obj=event, update_data=update_data, commit=False
        )
        await db.commit()
        return event
    except ValueError as ex:
        await db.rollback()
        raise ex
