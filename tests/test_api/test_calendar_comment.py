from typing import Callable

from httpx import AsyncClient

from models.calendar import CalendarEvent, CalendarEventComment
from models.user import User
from schemas.calendar.comments import CommentCreate

ROOT_ENDPOINT = "/ch/v1/calendar/comment/"


class TestCalendarCommentApi:
    async def test_get_multi(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        calendar_event_fixture: CalendarEvent,
        calendar_comment_fixture: CalendarEventComment,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}event/{calendar_event_fixture.id}/"
        response = await http_client.get(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 1

    async def test_get_multi_invalid_event(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}event/{999}/"
        response = await http_client.get(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 404

    async def test_get(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        calendar_comment_fixture: CalendarEventComment,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{calendar_comment_fixture.id}/"
        response = await http_client.get(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert calendar_comment_fixture.text == response_data["text"]

    async def test_get_invalid_comment(
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
        )
        assert response.status_code == 404

    async def test_create(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        calendar_event_fixture: CalendarEvent,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{calendar_event_fixture.id}/"
        create_data = CommentCreate(text="Test comment text")
        response = await http_client.post(
            endpoint,
            json=create_data.model_dump(),
            headers=user_auth_headers,
        )
        assert response.status_code == 201
        response_data = response.json()
        assert create_data.text == response_data["text"]

    async def test_create_with_invalid_event(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{999}/"
        create_data = CommentCreate(text="Test comment text")
        response = await http_client.post(
            endpoint,
            json=create_data.model_dump(),
            headers=user_auth_headers,
        )
        assert response.status_code == 404

    async def test_create_by_participant(
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
        create_data = CommentCreate(text="Test comment text")
        response = await http_client.post(
            endpoint,
            json=create_data.model_dump(),
            headers=another_user_auth_headers,
        )
        assert response.status_code == 201
        response_data = response.json()
        assert create_data.text == response_data["text"]

    async def test_update(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        calendar_comment_fixture: CalendarEventComment,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{calendar_comment_fixture.id}/"
        update_data = CommentCreate(text="Test comment text")
        response = await http_client.patch(
            endpoint,
            json=update_data.model_dump(),
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert update_data.text == response_data["text"]

    async def test_update_invalid_comment(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{999}/"
        update_data = CommentCreate(text="Test comment text")
        response = await http_client.patch(
            endpoint,
            json=update_data.model_dump(),
            headers=user_auth_headers,
        )
        assert response.status_code == 404

    async def test_update_by_not_author(
        self,
        http_client: AsyncClient,
        user_fixture_2: User,
        calendar_comment_fixture: CalendarEventComment,
        get_auth_headers: Callable,
    ) -> None:
        another_user_auth_headers = await get_auth_headers(user_fixture_2)
        endpoint = f"{ROOT_ENDPOINT}{calendar_comment_fixture.id}/"
        update_data = CommentCreate(text="Test comment text")
        response = await http_client.patch(
            endpoint,
            json=update_data.model_dump(),
            headers=another_user_auth_headers,
        )
        assert response.status_code == 403

    async def test_delete(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        calendar_comment_fixture: CalendarEventComment,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{calendar_comment_fixture.id}/"
        response = await http_client.delete(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 204

        response = await http_client.get(endpoint, headers=user_auth_headers)
        assert response.status_code == 404

    async def test_delete_invalid_comment(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{999}/"
        response = await http_client.delete(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 404

    async def test_delete_by_not_author(
        self,
        http_client: AsyncClient,
        user_fixture_2: User,
        calendar_comment_fixture: CalendarEventComment,
        get_auth_headers: Callable,
    ) -> None:
        another_user_auth_headers = await get_auth_headers(user_fixture_2)
        endpoint = f"{ROOT_ENDPOINT}{calendar_comment_fixture.id}/"
        response = await http_client.delete(
            endpoint,
            headers=another_user_auth_headers,
        )
        assert response.status_code == 403
