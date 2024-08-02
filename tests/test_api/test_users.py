from typing import Callable

from httpx import AsyncClient
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession

from models import Timezone, User
from schemas.user.user import UserCreate, UserUpdate, UserUpdateLinkPermission
from services.user import user_service
from services.user.completeness import update_user_completeness
from schemas.user.user_contact_info import ContactInfoParsed
from schemas.user.user_info import UserInfoCreateUpdate
from services.user.user_info import create_update_user_info

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
        mock_update_user_completeness_fixture: MockerFixture,
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
        mock_update_user_completeness_fixture: MockerFixture,
    ):
        mocked_method = mocker.patch(
            "utilities.email_client.EmailClient.send_mail",
        )
        mocked_method.return_value = None

        update_data = UserUpdate(
            first_name="Updated first name",
            schedule={
                "monday": "10:00-12:00",
                "tuesday": "12:00-18:00",
                "timezone": {"tzcode": "Milan", "utc": "+11:00"},
            },
        )
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
        mock_update_user_completeness_fixture: MockerFixture,
    ):
        mocked_method = mocker.patch(
            "utilities.email_client.EmailClient.send_mail",
        )
        mocked_method.return_value = None

        update_data = UserUpdate(timezone={"tzcode": "Moscow", "utc": "+11"})
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.patch(
            ROOT_ENDPOINT,
            json=update_data.model_dump(exclude_unset=True),
            headers=user_auth_headers,
        )
        assert response.status_code == 200

        response_data = response.json()
        assert (
            response_data["timezone"]["tzcode"] == update_data.timezone.tzcode
        )

    async def test_update_timezone_to_null(
        self,
        user_fixture: User,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        timezone_fixture: Timezone,
        mocker: MockerFixture,
        mock_update_user_completeness_fixture: MockerFixture,
    ):
        mocked_method = mocker.patch(
            "utilities.email_client.EmailClient.send_mail",
        )
        mocked_method.return_value = None

        update_data = UserUpdate(timezone=None)
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.patch(
            ROOT_ENDPOINT,
            json=update_data.model_dump(exclude_unset=True),
            headers=user_auth_headers,
        )
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["timezone"] is None

    async def test_update_external_link_permission(
        self,
        user_fixture: User,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ):
        endpoint = f"{ROOT_ENDPOINT}external_link/"
        user_auth_headers = await get_auth_headers(user_fixture)
        update_data = UserUpdateLinkPermission(external_link_permission=True)
        response = await http_client.patch(
            endpoint,
            json=update_data.model_dump(),
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["external_link_permission"] is True

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

        endpoint = f"{ROOT_ENDPOINT}{user_fixture.uid!s}/"
        response = await http_client.get(endpoint, headers=user_auth_headers)
        assert response.status_code == 404

    async def test_user_completeness(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        async_session: AsyncSession,
    ):
        await update_user_completeness(
            db=async_session, user_id=user_fixture.id
        )

        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}completeness/"
        response = await http_client.get(endpoint, headers=user_auth_headers)
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["main"] == 23
        assert response_data["contacts"] == 0
        user_update_data = UserUpdate(
            languages=["en", "ru"],
            timezone={"tzcode": "Moscow", "utc": "+4"},
        )
        user_contact_update_data = UserInfoCreateUpdate(
            links=[{"name": "example", "url": "http://example.com"}],
            contact_info=ContactInfoParsed(email="ex@mp.le"),
        )

        await user_service.update_user(
            db=async_session,
            user=user_fixture,
            update_schema=user_update_data,
        )
        await create_update_user_info(
            db=async_session,
            schema=user_contact_update_data,
            user_uid=user_fixture.uid,
        )

        await update_user_completeness(
            db=async_session, user_id=user_fixture.id
        )

        response = await http_client.get(endpoint, headers=user_auth_headers)
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["main"] == 38
        assert response_data["contacts"] == 67
