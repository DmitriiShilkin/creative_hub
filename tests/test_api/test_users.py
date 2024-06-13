from typing import Callable

from httpx import AsyncClient
from pytest_mock import MockerFixture

from models import Timezone, User
from schemas.user.user import UserCreate, UserUpdate

ROOT_ENDPOINT = "/ch/v1/user/"


class TestUserApi:
    async def test_get_user(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        get_auth_headers: Callable,
    ):
        endpoint = f"{ROOT_ENDPOINT}{user_fixture.uid}/"
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.get(endpoint, headers=user_auth_headers)
        assert response.status_code == 200

        response_data = response.json()
        assert str(user_fixture.uid) == response_data["uid"]

    async def test_user_profile(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        get_auth_headers: Callable,
    ):
        endpoint = f"{ROOT_ENDPOINT}profile/"
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.get(endpoint, headers=user_auth_headers)
        assert response.status_code == 200

        response_data = response.json()
        assert str(user_fixture.uid) == response_data["uid"]

    async def test_create_user(
        self,
        http_client: AsyncClient,
        mocker: MockerFixture,
    ):
        mocked_method = mocker.patch(
            "utilities.email_client.EmailClient.send_mail",
        )
        mocked_method.return_value = None

        new_user_data = UserCreate(
            username="Just_created_user",
            first_name="Just_created",
            second_name="User",
            email="test_user_created@gmail.com",
            password="password",
        )
        response = await http_client.post(
            ROOT_ENDPOINT, json=new_user_data.model_dump()
        )
        assert response.status_code == 201

        response_data = response.json()
        assert new_user_data.email == response_data["email"]

    async def test_update_user(
        self,
        user_fixture: User,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        mocker: MockerFixture,
    ):
        mocked_method = mocker.patch(
            "utilities.email_client.EmailClient.send_mail",
        )
        mocked_method.return_value = None

        update_data = UserUpdate(first_name="Updated first name")
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.patch(
            ROOT_ENDPOINT,
            json=update_data.model_dump(exclude_unset=True),
            headers=user_auth_headers,
        )
        assert response.status_code == 200

        response_data = response.json()
        assert update_data.first_name == response_data["first_name"]

    async def test_update_timezone(
        self,
        user_fixture: User,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        timezone_fixture: Timezone,
        mocker: MockerFixture,
    ):
        mocked_method = mocker.patch(
            "utilities.email_client.EmailClient.send_mail",
        )
        mocked_method.return_value = None

        update_data = UserUpdate(timezone_id=timezone_fixture.id)
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.patch(
            ROOT_ENDPOINT,
            json=update_data.model_dump(exclude_unset=True),
            headers=user_auth_headers,
        )
        assert response.status_code == 200

        response_data = response.json()
        assert "timezone" in response_data

    async def test_update_invalid_timezone(
        self,
        user_fixture: User,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        mocker: MockerFixture,
    ):
        mocked_method = mocker.patch(
            "utilities.email_client.EmailClient.send_mail",
        )
        mocked_method.return_value = None

        update_data = UserUpdate(timezone_id=999)
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.patch(
            ROOT_ENDPOINT,
            json=update_data.model_dump(exclude_unset=True),
            headers=user_auth_headers,
        )
        assert response.status_code == 404

    async def test_delete_user(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        get_auth_headers: Callable,
        mocker: MockerFixture,
    ):
        mocked_method = mocker.patch(
            "utilities.email_client.EmailClient.send_mail",
        )
        mocked_method.return_value = None

        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.delete(
            ROOT_ENDPOINT, headers=user_auth_headers
        )
        assert response.status_code == 204

        endpoint = f"{ROOT_ENDPOINT}{str(user_fixture.uid)}/"
        response = await http_client.get(endpoint, headers=user_auth_headers)
        assert response.status_code == 404
