from datetime import datetime, timedelta, UTC

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from constants.event import EventType, RegistrationEndType
from constants.i18n import EventLanguage
from crud.event import crud_event
from crud.event_participants import crud_event_participants
from models import City, Event, Organisation, Specialization, Timezone, User
from schemas.event import EventCreateDB, EventParticipantCreate


@pytest_asyncio.fixture
async def event_fixture(
    async_session: AsyncSession,
    user_fixture: User,
    user_fixture_2: User,
    specialization_fixture: Specialization,
    city_fixture: City,
    organisation_fixture: Organisation,
    timezone_fixture: Timezone,
) -> Event:
    schema = EventCreateDB(
        creator_id=user_fixture.id,
        photo=None,
        event_cover=None,
        title="Test event",
        description="test description",
        language=EventLanguage.ENG,
        extra_languages=[EventLanguage.FR],
        event_type=EventType.DEMO_DAY,
        is_free=True,
        is_online=True,
        timezone_id=timezone_fixture.id,
        city_id=city_fixture.id,
        online_links=["https://wwww.creativehub.com/"],
        start_datetime=datetime.now(tz=UTC) + timedelta(days=5),
        end_datetime=datetime.now(tz=UTC) + timedelta(days=10),
        registration_end_type=RegistrationEndType.AT_EVENT_START,
        is_draft=False,
        is_archived=False,
    )
    event = await crud_event.create(
        db=async_session, create_schema=schema, commit=False
    )
    event.organizers = [user_fixture]
    event.speakers = [user_fixture]
    event.specializations = [specialization_fixture]
    event.organisations = [organisation_fixture]

    await crud_event_participants.create(
        db=async_session,
        create_schema=EventParticipantCreate(
            user_id=user_fixture_2.id,
            event_id=event.id,
        ),
    )
    await async_session.commit()
    return event


@pytest_asyncio.fixture
async def event_fixture_2(
    async_session: AsyncSession,
    user_fixture: User,
    specialization_fixture_2: Specialization,
    city_fixture: City,
    organisation_fixture: Organisation,
    timezone_fixture: Timezone,
) -> Event:
    schema = EventCreateDB(
        creator_id=user_fixture.id,
        photo=None,
        event_cover=None,
        title="Test event 2",
        description="test description 2",
        extra_languages=[EventLanguage.ENG],
        language=EventLanguage.RUS,
        event_type=EventType.CONCERT,
        is_free=True,
        is_online=False,
        city_id=city_fixture.id,
        online_links=["https://wwww.creativehub_2.com/"],
        start_datetime=datetime.now(tz=UTC) + timedelta(days=5),
        end_datetime=datetime.now(tz=UTC) + timedelta(days=10),
        registration_end_type=RegistrationEndType.AT_EVENT_START,
        is_draft=True,
        is_archived=False,
        timezone_id=timezone_fixture.id,
    )
    event = await crud_event.create(
        db=async_session, create_schema=schema, commit=False
    )

    event.organizers = [user_fixture]
    event.speakers = [user_fixture]
    event.specializations = [specialization_fixture_2]
    event.organisations = [organisation_fixture]

    await async_session.commit()
    await async_session.refresh(event)

    return event


@pytest_asyncio.fixture
async def event_fixture_3(
    async_session: AsyncSession,
    user_fixture: User,
    specialization_fixture_2: Specialization,
    city_fixture: City,
    organisation_fixture: Organisation,
    timezone_fixture: Timezone,
) -> Event:
    schema = EventCreateDB(
        creator_id=user_fixture.id,
        photo=None,
        event_cover=None,
        title="Test event 3",
        description="test description 3",
        extra_languages=[EventLanguage.ENG],
        language=EventLanguage.RUS,
        event_type=EventType.CONCERT,
        is_free=True,
        is_online=False,
        city_id=city_fixture.id,
        online_links=["https://wwww.creativehub_2.com/"],
        start_datetime=datetime.now(tz=UTC) + timedelta(days=5),
        end_datetime=datetime.now(tz=UTC) + timedelta(days=10),
        registration_end_type=RegistrationEndType.AT_EVENT_START,
        is_draft=False,
        is_archived=True,
        timezone_id=timezone_fixture.id,
    )
    event = await crud_event.create(
        db=async_session, create_schema=schema, commit=False
    )

    event.organizers = [user_fixture]
    event.speakers = [user_fixture]
    event.specializations = [specialization_fixture_2]
    event.organisations = [organisation_fixture]

    await async_session.commit()
    await async_session.refresh(event)

    return event
