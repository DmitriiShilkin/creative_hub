from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from models import User, UserExperience, UserSpecialization
from models.user.mentorship import Mentorship

ROOT_ENDPOINT = "/ch/v1/"


class TestUserCatalogAPI:
    async def test_read_user_specialists(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
        user_specialization_fixture: UserSpecialization,
        user_experience_fixture: UserExperience,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}user-specialists/"

        response = await http_client.get(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data[0]["specialization"] is not None
        assert response_data[0]["experience"] != []

    async def test_read_user_experts(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
        mentorship_fixture: Mentorship,
        user_experience_fixture: UserExperience,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}user-experts/"

        response = await http_client.get(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data[0]["mentorship"] is not None
        assert response_data[0]["experience"] != []
