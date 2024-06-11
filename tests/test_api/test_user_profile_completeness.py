from typing import Callable

from httpx import AsyncClient

from models.user import User
from models.user.profile_completeness import ProfileCompleteness
from schemas.user.profile_completeness import ProfileCompletenessUpdate

ROOT_ENDPOINT = "/ch/v1/profile-completeness/"


class TestUserProfileCompletenessApi:
    async def test_get(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        profile_completeness_fixture: ProfileCompleteness,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.get(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert (
            profile_completeness_fixture.main_percentage
            == response_data["main_percentage"]
        )

    async def test_update(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        profile_completeness_fixture: ProfileCompleteness,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        update_data = ProfileCompletenessUpdate(
            main_percentage=75,
            contacts_percentage=100,
            education_percentage=100,
            experience_percentage=100,
            mentorship_percentage=0,
        )
        response = await http_client.patch(
            ROOT_ENDPOINT,
            json=update_data.model_dump(),
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert update_data.main_percentage == response_data["main_percentage"]
