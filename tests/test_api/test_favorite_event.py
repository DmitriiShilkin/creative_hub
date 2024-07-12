from typing import Callable, List

from httpx import AsyncClient

from models import Event, User
from schemas.event import EventSimpleResponse

ROOT_ENDPOINT = "/ch/v1/favorite-events/"


class TestFavoriteEvent:
    async def test_read_favorite_event(
        self,
        user_fixture: User,
        event_fixture: Event,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        event_favorites_list_fixture: List[EventSimpleResponse],
    ):
        assert event_favorites_list_fixture[0].title == event_fixture.title

        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.get(
            ROOT_ENDPOINT, headers=user_auth_headers
        )
        response_data = response.json()
        assert response.status_code == 200, response.text
        assert response_data["objects"][0]["title"] == event_fixture.title
        assert (
            response_data["objects"][0]["description"]
            == event_fixture.description
        )

    async def test_read_favorite_event_unauthorized(
        self,
        event_fixture: Event,
        http_client: AsyncClient,
        event_favorites_list_fixture: List[EventSimpleResponse],
    ):
        assert event_favorites_list_fixture[0].id == event_fixture.id

        response = await http_client.get(ROOT_ENDPOINT)
        assert response.status_code == 401, response.text

    async def test_add_favorite_event(
        self,
        user_fixture: User,
        event_fixture: Event,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ):
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.post(
            f"{ROOT_ENDPOINT}{event_fixture.id}/",
            headers=user_auth_headers,
        )
        assert response.status_code == 201, response.text

    async def test_add_favorite_event_unauthorized(
        self,
        event_fixture: Event,
        http_client: AsyncClient,
    ):
        response = await http_client.post(
            f"{ROOT_ENDPOINT}{event_fixture.id}/"
        )
        assert response.status_code == 401, response.text

    async def test_add_favorite_event_not_found(
        self,
        user_fixture: User,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ):
        user_auth_headers = await get_auth_headers(user_fixture)
        id_does_not_exists = 9999
        response = await http_client.post(
            f"{ROOT_ENDPOINT}{id_does_not_exists}/",
            headers=user_auth_headers,
        )
        assert response.status_code == 404, response.text

    async def test_favorite_event_already_added(
        self,
        user_fixture: User,
        event_fixture: Event,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ):
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.post(
            f"{ROOT_ENDPOINT}{event_fixture.id}/",
            headers=user_auth_headers,
        )
        assert response.status_code == 201, response.text

        response_two = await http_client.post(
            f"{ROOT_ENDPOINT}{event_fixture.id}/",
            headers=user_auth_headers,
        )
        assert response_two.status_code == 400, response.text

    async def test_remove_favorite_event(
        self,
        user_fixture: User,
        event_fixture: Event,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        event_favorites_list_fixture: List[EventSimpleResponse],
    ):
        assert event_favorites_list_fixture[0].id == event_fixture.id

        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.delete(
            f"{ROOT_ENDPOINT}{event_fixture.id}/",
            headers=user_auth_headers,
        )
        assert response.status_code == 204, response.text

    async def test_remove_favorite_event_unauthorized(
        self,
        event_fixture: Event,
        http_client: AsyncClient,
        event_favorites_list_fixture: List[EventSimpleResponse],
    ):
        assert event_favorites_list_fixture[0].id == event_fixture.id

        response = await http_client.delete(
            f"{ROOT_ENDPOINT}{event_fixture.id}/",
        )
        assert response.status_code == 401, response.text

    async def test_remove_favorite_event_not_found(
        self,
        user_fixture: User,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ):
        id_does_not_exists = 9999
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.delete(
            f"{ROOT_ENDPOINT}{id_does_not_exists}/",
            headers=user_auth_headers,
        )
        assert response.status_code == 404, response.text
