import uuid
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from models import User, City, UserExperience
from constants.month import Month
from schemas.user.user_experience import (
    ExperienceCreate,
    ExperienceUpdate,
)

ROOT_ENDPOINT = "/ch/v1/user-experience/"


class TestUserExperience:
    async def test_read_user_experience(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user: User,
    ) -> None:
        user_auth_headers = await get_auth_headers(user)
        endpoint = f"{ROOT_ENDPOINT}{user.uid}/"

        response = await http_client.get(
            endpoint, headers=user_auth_headers,
        )
        assert response.status_code == 200

        response = await http_client.get(
            f"{ROOT_ENDPOINT}{uuid.uuid4()}/",
            headers=user_auth_headers,
        )
        assert response.status_code == 404

    async def test_create_user_experience(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user: User,
        city: City,
    ) -> None:
        user_auth_headers = await get_auth_headers(user)
        data = ExperienceCreate(
            company_name="Test company name",
            job_title="Test job title",
            start_month=Month.February,
            start_year=2024,
            still_working=True,
            city_id=city.id,
        )

        response = await http_client.post(
            ROOT_ENDPOINT, headers=user_auth_headers,
            json=[data.model_dump()],
        )
        assert response.status_code == 201
        response_data = response.json()
        assert response_data[0]["job_title"] == data.job_title

    async def test_create_user_experience_with_invalid_city_id(
            self,
            http_client: AsyncSession,
            get_auth_headers: Callable,
            user: User,
    ) -> None:
        user_auth_headers = await get_auth_headers(user)
        data = ExperienceCreate(
            company_name="Test company name",
            job_title="Test job title",
            start_month=Month.February,
            start_year=2024,
            city_id=999,
            still_working=True,
        )

        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            json=[data.model_dump()],
        )
        assert response.status_code == 404

    async def test_update_user_experience(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user: User,
        user_experience: UserExperience,
    ) -> None:
        user_auth_headers = await get_auth_headers(user)
        endpoint = f"{ROOT_ENDPOINT}{user_experience.id}/"
        data = ExperienceUpdate(
            job_title="Test another job title",
        )

        response = await http_client.patch(
            endpoint, headers=user_auth_headers,
            json=data.model_dump(exclude_unset=True),
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["job_title"] == data.job_title

    async def test_update_invalid_user_experience(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user: User,
    ) -> None:
        user_auth_headers = await get_auth_headers(user)
        endpoint = f"{ROOT_ENDPOINT}{999}/"
        data = ExperienceUpdate(
            job_title="Test another job title",
        )

        response = await http_client.patch(
            endpoint, headers=user_auth_headers,
            json=data.model_dump(exclude_unset=True),
        )
        assert response.status_code == 404

    async def test_update_user_experience_with_invalid_city_id(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user: User,
        user_experience: UserExperience,
    ) -> None:
        user_auth_headers = await get_auth_headers(user)
        endpoint = f"{ROOT_ENDPOINT}{user_experience.id}/"
        data = ExperienceUpdate(
            city_id=999,
        )

        response = await http_client.patch(
            endpoint, headers=user_auth_headers,
            json=data.model_dump(exclude_unset=True),
        )
        assert response.status_code == 404

    async def test_update_user_experience_with_invalid_company_name(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user: User,
        user_experience: UserExperience,
    ) -> None:
        user_auth_headers = await get_auth_headers(user)
        endpoint = f"{ROOT_ENDPOINT}{user_experience.id}/"
        data = ExperienceUpdate(
            company_name="",
        )

        response = await http_client.patch(
            endpoint, headers=user_auth_headers,
            json=data.model_dump(),
        )
        assert response.status_code == 422

    async def test_delete_user_experience(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user: User,
        user_experience: UserExperience,
    ) -> None:
        user_auth_headers = await get_auth_headers(user)
        endpoint = f"{ROOT_ENDPOINT}{user_experience.id}/"

        response = await http_client.delete(
            endpoint, headers=user_auth_headers,
        )
        assert response.status_code == 204

        endpoint = f"{ROOT_ENDPOINT}{user.uid}/"

        response = await http_client.get(
            endpoint, headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data == []

    async def test_delete_invalid_user_experience(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user: User,
    ) -> None:
        user_auth_headers = await get_auth_headers(user)
        endpoint = f"{ROOT_ENDPOINT}{999}/"

        response = await http_client.delete(
            endpoint, headers=user_auth_headers,
        )
        assert response.status_code == 404

    async def test_delete_user_experience_by_not_owner(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        another_user: User,
        user_experience: UserExperience,
    ) -> None:
        user_auth_headers = await get_auth_headers(another_user)
        endpoint = f"{ROOT_ENDPOINT}{user_experience.id}/"

        response = await http_client.delete(
            endpoint, headers=user_auth_headers,
        )
        assert response.status_code == 403
