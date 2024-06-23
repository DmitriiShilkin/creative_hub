import uuid
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from constants.user_specialization import Grade, Status
from models.user.specialization import Specialization
from models.user.user import User
from models.user.user_specialization import UserSpecialization
from schemas.user.user_specialization import (
    UserSpecializationCreate,
    UserSpecializationUpdate,
)

ROOT_ENDPOINT = "/ch/v1/user-specialization/"


class TestUserSpecialization:
    async def test_read_user_specialization(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
        user_fixture_2: User,
        user_specialization_fixture: UserSpecialization,
    ):
        auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{user_fixture.uid}/"

        response = await http_client.get(endpoint, headers=auth_headers)
        assert response.status_code == 200

        added_user_specialization = response.json()["grade"]
        assert added_user_specialization == user_specialization_fixture.grade

        # If user_fixture not found, returns 404
        no_user_uid = uuid.uuid4()
        response = await http_client.get(
            f"{ROOT_ENDPOINT}{no_user_uid}/",
            headers=auth_headers,
        )
        assert response.status_code == 404

        # If user don't have specialization, returns 404
        response = await http_client.get(
            f"{ROOT_ENDPOINT}{user_fixture_2.uid}/",
            headers=auth_headers,
        )
        assert response.status_code == 404

    async def test_create_user_specialization(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
        user_specialization_fixture: UserSpecialization,
        user_fixture_2: User,
        specialization_fixture: Specialization,
    ):
        auth_headers = await get_auth_headers(user_fixture_2)
        create_schema = UserSpecializationCreate(
            grade=Grade.senior,
            status=Status.no_searching,
            is_ready_to_move=False,
            is_ready_for_remote_work=False,
            specialization_ids=[
                specialization_fixture.id,
            ],
            descriptions=[{"description": "Специализация", "lang": "ru"}],
            keywords=[{"name": "UI"}],
        )
        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=auth_headers,
            json=create_schema.model_dump(),
        )
        assert response.status_code == 200

        added_specialization = response.json()["specializations"][0]["name"]
        assert added_specialization == specialization_fixture.name

        # If user already has a specialization,
        # returns their existing specialization.
        auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=auth_headers,
            json=create_schema.model_dump(),
        )
        assert response.status_code == 200

        returned_specialization = response.json()["grade"]
        assert returned_specialization == user_specialization_fixture.grade

    async def test_update_user_specialization(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
        user_specialization_fixture: UserSpecialization,
        user_fixture_2: User,
        specialization_fixture_2: Specialization,
    ):
        auth_headers = await get_auth_headers(user_fixture)
        update_data = UserSpecializationUpdate(
            grade=Grade.senior,
            status=Status.no_searching,
            is_ready_to_move=False,
            is_ready_for_remote_work=True,
            specialization_ids=[
                specialization_fixture_2.id,
            ],
            descriptions=[{"description": "Специализация", "lang": "ru"}],
            keywords=[{"name": "UI"}],
        )
        response = await http_client.put(
            ROOT_ENDPOINT,
            headers=auth_headers,
            json=update_data.model_dump(),
        )
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["grade"] == update_data.grade

        updated_specialization = response_data["specializations"][0]["name"]
        assert updated_specialization == specialization_fixture_2.name

        # If user_fixture don't have specialization, returns 404
        auth_headers = await get_auth_headers(user_fixture_2)
        response = await http_client.put(
            ROOT_ENDPOINT,
            headers=auth_headers,
            json=update_data.model_dump(),
        )
        assert response.status_code == 404
