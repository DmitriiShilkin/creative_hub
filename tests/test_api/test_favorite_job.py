from typing import Callable

from httpx import AsyncClient

from models import Job, User
from schemas.endpoints.paginated_response import JobPaginatedResponse

ROOT_ENDPOINT = "/ch/v1/favorite-jobs/"


class TestFavoriteJobAPI:
    async def test_read_favorite_job(
        self,
        user_fixture: User,
        job_fixture: Job,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        job_favorites_list_fixture: JobPaginatedResponse,
    ) -> None:
        assert job_favorites_list_fixture["objects"][0]["Job"] == job_fixture

        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.get(
            ROOT_ENDPOINT, headers=user_auth_headers
        )
        response_data = response.json()
        assert response.status_code == 200, response.text
        assert response_data["objects"][0]["name"] == job_fixture.name

    async def test_read_favorite_job_unauthorized(
        self,
        job_fixture: Job,
        http_client: AsyncClient,
        job_favorites_list_fixture: JobPaginatedResponse,
    ) -> None:
        assert job_favorites_list_fixture["objects"][0]["Job"] == job_fixture

        response = await http_client.get(ROOT_ENDPOINT)
        assert response.status_code == 401, response.text

    async def test_add_favorite_job(
        self,
        user_fixture: User,
        job_fixture: Job,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.post(
            f"{ROOT_ENDPOINT}{job_fixture.id}/",
            headers=user_auth_headers,
        )
        assert response.status_code == 201, response.text

    async def test_add_favorite_job_unauthorized(
        self,
        job_fixture: Job,
        http_client: AsyncClient,
    ) -> None:
        response = await http_client.post(f"{ROOT_ENDPOINT}{job_fixture.id}/")
        assert response.status_code == 401, response.text

    async def test_add_invalid_favorite_job(
        self,
        user_fixture: User,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.post(
            f"{ROOT_ENDPOINT}{999}/",
            headers=user_auth_headers,
        )
        assert response.status_code == 404, response.text

    async def test_favorite_job_already_added(
        self,
        user_fixture: User,
        job_fixture: Job,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.post(
            f"{ROOT_ENDPOINT}{job_fixture.id}/",
            headers=user_auth_headers,
        )
        assert response.status_code == 201, response.text

        response = await http_client.post(
            f"{ROOT_ENDPOINT}{job_fixture.id}/",
            headers=user_auth_headers,
        )
        assert response.status_code == 400, response.text

    async def test_remove_favorite_job(
        self,
        user_fixture: User,
        job_fixture: Job,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        job_favorites_list_fixture: JobPaginatedResponse,
    ) -> None:
        assert job_favorites_list_fixture["objects"][0]["Job"] == job_fixture

        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.delete(
            f"{ROOT_ENDPOINT}{job_fixture.id}/",
            headers=user_auth_headers,
        )
        assert response.status_code == 204, response.text

    async def test_remove_favorite_job_unauthorized(
        self,
        job_fixture: Job,
        http_client: AsyncClient,
        job_favorites_list_fixture: JobPaginatedResponse,
    ) -> None:
        assert job_favorites_list_fixture["objects"][0]["Job"] == job_fixture

        response = await http_client.delete(
            f"{ROOT_ENDPOINT}{job_fixture.id}/",
        )
        assert response.status_code == 401, response.text

    async def test_remove_invalid_favorite_job(
        self,
        user_fixture: User,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.delete(
            f"{ROOT_ENDPOINT}{999}/",
            headers=user_auth_headers,
        )
        assert response.status_code == 404, response.text
