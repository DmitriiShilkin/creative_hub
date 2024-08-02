from datetime import datetime, timedelta

import pytest_asyncio
from pytz import utc
from sqlalchemy.ext.asyncio import AsyncSession

from constants.calendar.event import (
    CalendarEventPriority,
    CalendarEventRepeatability,
    CalendarEventType,
)
from crud.calendar.event import calendar_event_crud
from models import User
from models.calendar import CalendarEvent
from schemas.calendar.event import CalendarEventCreateDB
from utilities.validators.calendar_event import check_participants


@pytest_asyncio.fixture
async def calendar_event_fixture(
    async_session: AsyncSession, user_fixture: User
) -> CalendarEvent:
    now = datetime.now(utc)
    if now.month == (now + timedelta(days=1, hours=2)).month:
        start_time = now + timedelta(days=1, hours=1)
    else:
        start_time = now - timedelta(days=1) + timedelta(hours=1)
    schema = CalendarEventCreateDB(
        title="Calendar event title",
        event_type=CalendarEventType.NO_CATEGORY,
        priority=CalendarEventPriority.WITHOUT_PRIORITY,
        repeatability=CalendarEventRepeatability.NO_REPEATS,
        start_time=start_time,
        end_time=start_time + timedelta(hours=1),
        description="Calendar event description",
        organizer_id=user_fixture.id,
    )
    new_calendar_event = await calendar_event_crud.create(
        db=async_session,
        create_schema=schema,
    )
    return new_calendar_event


@pytest_asyncio.fixture
async def calendar_event_with_participant_fixture(
    async_session: AsyncSession,
    user_fixture: User,
    user_fixture_2: User,
) -> CalendarEvent:
    schema = CalendarEventCreateDB(
        title="Another calendar event title",
        event_type=CalendarEventType.NO_CATEGORY,
        priority=CalendarEventPriority.WITHOUT_PRIORITY,
        repeatability=CalendarEventRepeatability.NO_REPEATS,
        start_time=datetime.now(utc) + timedelta(days=1, hours=1),
        end_time=datetime.now(utc) + timedelta(days=1, hours=2),
        description="Calendar event description",
        organizer_id=user_fixture.id,
    )
    new_calendar_event = await calendar_event_crud.create(
        db=async_session, create_schema=schema, commit=False
    )
    new_calendar_event.participants = await check_participants(
        db=async_session,
        user_id=user_fixture.id,
        participants=[user_fixture_2.username],
    )
    await async_session.commit()
    return new_calendar_event
