from datetime import datetime, timedelta
from typing import Callable

from httpx import AsyncClient
from pytz import utc

from constants.calendar.event import (
    CalendarEventPriority,
    CalendarEventRepeatability,
    CalendarEventType,
)
from constants.calendar.period import CalendarEventPeriod
from models.calendar import CalendarEvent
from models.user import User
from schemas.calendar.event import CalendarEventCreate, CalendarEventUpdate

ROOT_ENDPOINT = "/ch/v1/calendar/event/"


class TestCalendarEventApi:
    async def test_get_multi_by_period(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        calendar_event_fixture: CalendarEvent,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.get(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            params={
                "period": CalendarEventPeriod.MONTH,
            },
        )
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 1

        response = await http_client.get(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            params={
                "period": CalendarEventPeriod.DAY,
            },
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data == []

    async def test_get(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        calendar_event_fixture: CalendarEvent,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{calendar_event_fixture.id}/"
        response = await http_client.get(
            endpoint,
            headers=user_auth_headers,
            params={
                "period": CalendarEventPeriod.MONTH,
            },
        )
        assert response.status_code == 200
        response_data = response.json()
        assert calendar_event_fixture.title == response_data["title"]

    async def test_get_invalid_event(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{999}/"
        response = await http_client.get(
            endpoint,
            headers=user_auth_headers,
            params={
                "period": CalendarEventPeriod.MONTH,
            },
        )
        assert response.status_code == 404

    async def test_create(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        user_fixture_2: User,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        create_data = CalendarEventCreate(
            title="Test calendar event title",
            event_type=CalendarEventType.NO_CATEGORY,
            priority=CalendarEventPriority.WITHOUT_PRIORITY,
            repeatability=CalendarEventRepeatability.NO_REPEATS,
            start_time=datetime.now(utc) + timedelta(hours=1),
            end_time=datetime.now(utc) + timedelta(hours=2),
            description="Test calendar event description",
            participants=[
                user_fixture_2.first_name + user_fixture_2.second_name
            ],
        )
        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            json=create_data.model_dump(mode="json"),
        )
        assert response.status_code == 201

        response_data = response.json()
        assert create_data.title == response_data["title"]

    async def test_create_invalid_participant(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        user_fixture_2: User,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        create_data = CalendarEventCreate(
            title="Test calendar event title",
            event_type=CalendarEventType.NO_CATEGORY,
            priority=CalendarEventPriority.WITHOUT_PRIORITY,
            repeatability=CalendarEventRepeatability.NO_REPEATS,
            start_time=datetime.now(utc) + timedelta(hours=1),
            end_time=datetime.now(utc) + timedelta(hours=2),
            description="Test calendar event description",
            participants=[user_fixture.first_name + user_fixture.second_name],
        )
        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            json=create_data.model_dump(mode="json"),
        )
        assert response.status_code == 400

        create_data = CalendarEventCreate(
            title="Test calendar event title",
            event_type=CalendarEventType.NO_CATEGORY,
            priority=CalendarEventPriority.WITHOUT_PRIORITY,
            repeatability=CalendarEventRepeatability.NO_REPEATS,
            start_time=datetime.now(utc) + timedelta(hours=1),
            end_time=datetime.now(utc) + timedelta(hours=2),
            description="Test calendar event description",
            participants=["Test invalid participant"],
        )
        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            json=create_data.model_dump(mode="json"),
        )
        assert response.status_code == 400

        create_data = CalendarEventCreate(
            title="Test calendar event title",
            event_type=CalendarEventType.NO_CATEGORY,
            priority=CalendarEventPriority.WITHOUT_PRIORITY,
            repeatability=CalendarEventRepeatability.NO_REPEATS,
            start_time=datetime.now(utc) + timedelta(hours=1),
            end_time=datetime.now(utc) + timedelta(hours=2),
            description="Test calendar event description",
            participants=[
                user_fixture_2.first_name + user_fixture_2.second_name,
                user_fixture_2.username,
            ],
        )
        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            json=create_data.model_dump(mode="json"),
        )
        assert response.status_code == 400

    async def test_create_invalid_time(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        create_data = CalendarEventCreate(
            title="Test calendar event title",
            event_type=CalendarEventType.NO_CATEGORY,
            priority=CalendarEventPriority.WITHOUT_PRIORITY,
            repeatability=CalendarEventRepeatability.NO_REPEATS,
            start_time=datetime.now(utc) - timedelta(hours=1),
            end_time=datetime.now(utc) + timedelta(hours=1),
            description="Test calendar event description",
            participants=[],
        )
        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            json=create_data.model_dump(mode="json"),
        )
        assert response.status_code == 400

        create_data = CalendarEventCreate(
            title="Test calendar event title",
            event_type=CalendarEventType.NO_CATEGORY,
            priority=CalendarEventPriority.WITHOUT_PRIORITY,
            repeatability=CalendarEventRepeatability.NO_REPEATS,
            start_time=datetime.now(utc) + timedelta(hours=1),
            end_time=datetime.now(utc) - timedelta(hours=1),
            description="Test calendar event description",
            participants=[],
        )
        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            json=create_data.model_dump(mode="json"),
        )
        assert response.status_code == 400

        equal_time = datetime.now(utc) + timedelta(hours=1)
        create_data = CalendarEventCreate(
            title="Test calendar event title",
            event_type=CalendarEventType.NO_CATEGORY,
            priority=CalendarEventPriority.WITHOUT_PRIORITY,
            repeatability=CalendarEventRepeatability.NO_REPEATS,
            start_time=equal_time,
            end_time=equal_time,
            description="Test calendar event description",
            participants=[],
        )
        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            json=create_data.model_dump(mode="json"),
        )
        assert response.status_code == 400

        create_data = CalendarEventCreate(
            title="Test calendar event title",
            event_type=CalendarEventType.NO_CATEGORY,
            priority=CalendarEventPriority.WITHOUT_PRIORITY,
            repeatability=CalendarEventRepeatability.NO_REPEATS,
            start_time=datetime.now(utc) + timedelta(hours=2),
            end_time=datetime.now(utc) + timedelta(hours=1),
            description="Test calendar event description",
            participants=[],
        )
        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            json=create_data.model_dump(mode="json"),
        )
        assert response.status_code == 400

    async def test_update(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        user_fixture_2: User,
        calendar_event_fixture: CalendarEvent,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{calendar_event_fixture.id}/"
        update_data = CalendarEventUpdate(
            title="Test calendar event title",
            participants=[
                user_fixture_2.first_name + user_fixture_2.second_name
            ],
        )
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            json=update_data.model_dump(exclude_unset=True),
        )
        assert response.status_code == 200

        response_data = response.json()
        assert update_data.title == response_data["title"]

    async def test_update_invalid_event(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{999}/"
        update_data = CalendarEventUpdate(
            title="Test calendar event title",
        )
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            json=update_data.model_dump(exclude_unset=True),
        )
        assert response.status_code == 404

    async def test_update_by_not_organizer(
        self,
        http_client: AsyncClient,
        user_fixture_2: User,
        calendar_event_with_participant_fixture: CalendarEvent,
        get_auth_headers: Callable,
    ) -> None:
        another_user_auth_headers = await get_auth_headers(user_fixture_2)
        endpoint = (
            f"{ROOT_ENDPOINT}{calendar_event_with_participant_fixture.id}/"
        )
        update_data = CalendarEventUpdate(
            title="Test calendar event title",
        )
        response = await http_client.patch(
            endpoint,
            headers=another_user_auth_headers,
            json=update_data.model_dump(exclude_unset=True),
        )
        assert response.status_code == 403

    async def test_update_invalid_participant(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        user_fixture_2: User,
        calendar_event_fixture: CalendarEvent,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{calendar_event_fixture.id}/"
        update_data = CalendarEventUpdate(
            participants=[user_fixture.first_name + user_fixture.second_name],
        )
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            json=update_data.model_dump(exclude_unset=True),
        )
        assert response.status_code == 400

        update_data = CalendarEventUpdate(
            participants=["Test invalid participant"],
        )
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            json=update_data.model_dump(exclude_unset=True),
        )
        assert response.status_code == 400

        update_data = CalendarEventUpdate(
            participants=[
                user_fixture_2.first_name + user_fixture_2.second_name,
                user_fixture_2.username,
            ],
        )
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            json=update_data.model_dump(exclude_unset=True, mode="json"),
        )
        assert response.status_code == 400

    async def test_update_invalid_time(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        calendar_event_fixture: CalendarEvent,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{calendar_event_fixture.id}/"
        update_data = CalendarEventUpdate(
            start_time=datetime.now(utc) - timedelta(hours=1),
        )
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            json=update_data.model_dump(exclude_unset=True, mode="json"),
        )
        assert response.status_code == 400

        update_data = CalendarEventUpdate(
            end_time=datetime.now(utc) - timedelta(hours=1),
        )
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            json=update_data.model_dump(exclude_unset=True, mode="json"),
        )
        assert response.status_code == 400

        equal_time = datetime.now(utc) + timedelta(hours=1)
        update_data = CalendarEventUpdate(
            start_time=equal_time,
            end_time=equal_time,
        )
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            json=update_data.model_dump(exclude_unset=True, mode="json"),
        )
        assert response.status_code == 400

        update_data = CalendarEventUpdate(
            start_time=datetime.now(utc) + timedelta(hours=2),
            end_time=datetime.now(utc) + timedelta(hours=1),
        )
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            json=update_data.model_dump(exclude_unset=True, mode="json"),
        )
        assert response.status_code == 400

        update_data = CalendarEventUpdate(
            start_time=datetime.now(utc) + timedelta(days=1, hours=3),
        )
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            json=update_data.model_dump(exclude_unset=True, mode="json"),
        )
        assert response.status_code == 400

        update_data = CalendarEventUpdate(
            end_time=datetime.now(utc) + timedelta(days=1, minutes=30),
        )
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            json=update_data.model_dump(exclude_unset=True, mode="json"),
        )
        assert response.status_code == 400

    async def test_delete(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        calendar_event_fixture: CalendarEvent,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{calendar_event_fixture.id}/"
        response = await http_client.delete(
            endpoint, headers=user_auth_headers
        )
        assert response.status_code == 204

        response = await http_client.get(endpoint, headers=user_auth_headers)
        assert response.status_code == 404

    async def test_delete_invalid_event(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{999}/"
        response = await http_client.delete(
            endpoint, headers=user_auth_headers
        )
        assert response.status_code == 404

    async def test_delete_by_not_organizer(
        self,
        http_client: AsyncClient,
        user_fixture_2: User,
        calendar_event_with_participant_fixture: CalendarEvent,
        get_auth_headers: Callable,
    ) -> None:
        another_user_auth_headers = await get_auth_headers(user_fixture_2)
        endpoint = (
            f"{ROOT_ENDPOINT}{calendar_event_with_participant_fixture.id}/"
        )
        response = await http_client.delete(
            endpoint, headers=another_user_auth_headers
        )
        assert response.status_code == 403
