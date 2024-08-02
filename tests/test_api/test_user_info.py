from typing import Callable

from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession

from models import Link, PrivateSite, User
from schemas.user.user_info import UserInfoCreateUpdate

ROOT_ENDPOINT = "/ch/v1/user/"


class TestUpdateUserInfo:
    async def test_create(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
        mock_update_user_completeness_fixture: MockerFixture,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        link = {"name": "Test", "url": "https://example.com/"}
        contact_info = {
            "email": "example@yandex.ru",
            "phone_code": "+123",
            "phone_number": "1234567788",
        }
        private_site = {
            "name": "Test name",
            "url": "https://test_private_site.com/",
        }
        data = UserInfoCreateUpdate(
            links=[link],
            private_site=private_site,
            contact_info=contact_info,
        )
        response = await http_client.put(
            ROOT_ENDPOINT, headers=user_auth_headers, json=data.model_dump()
        )
        assert response.status_code == 200
        response_data = response.json()
        assert link["name"] in response_data["links"][0].values()
        assert private_site["name"] in response_data["private_site"].values()
        assert contact_info["email"] in response_data["contact_info"].values()

    async def test_create_without_private_site_schema(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
        mock_update_user_completeness_fixture: MockerFixture,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        link = {"name": "Test", "url": "https://example.com/"}
        contact_info = {
            "email": "example@yandex.ru",
            "phone_code": "+123",
            "phone_number": "1234567788",
        }
        data = UserInfoCreateUpdate(
            links=[link],
            contact_info=contact_info,
        )
        response = await http_client.put(
            ROOT_ENDPOINT, headers=user_auth_headers, json=data.model_dump()
        )
        assert response.status_code == 200
        response_data = response.json()
        assert link["name"] in response_data["links"][0].values()
        assert contact_info["email"] in response_data["contact_info"].values()

    async def test_update(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
        link_fixture: Link,
        private_site_fixture: PrivateSite,
        mock_update_user_completeness_fixture: MockerFixture,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        link = {
            "name": "Another Test",
            "url": "https://example.com/",
            "id": link_fixture.id,
        }
        contact_info = {
            "email": "example@yandex.ru",
            "phone_code": "+123",
            "phone_number": "1234567788",
        }
        private_site = {
            "name": "Another test name",
            "url": "https://test_private_site.com/",
        }
        data = UserInfoCreateUpdate(
            links=[link],
            private_site=private_site,
            contact_info=contact_info,
        )
        response = await http_client.put(
            ROOT_ENDPOINT, headers=user_auth_headers, json=data.model_dump()
        )
        assert response.status_code == 200
        response_data = response.json()
        assert link["name"] in response_data["links"][0].values()
        assert private_site["name"] in response_data["private_site"].values()
        assert contact_info["email"] in response_data["contact_info"].values()

    async def test_update_without_private_site_schema(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
        link_fixture: Link,
        private_site_fixture: PrivateSite,
        mock_update_user_completeness_fixture: MockerFixture,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        link = {
            "name": "Another Test",
            "url": "https://example.com/",
            "id": link_fixture.id,
        }
        contact_info = {
            "email": "example@yandex.ru",
            "phone_code": "+123",
            "phone_number": "1234567788",
        }
        data = UserInfoCreateUpdate(
            links=[link],
            contact_info=contact_info,
        )
        response = await http_client.put(
            ROOT_ENDPOINT, headers=user_auth_headers, json=data.model_dump()
        )
        assert response.status_code == 200
        response_data = response.json()
        assert link["name"] in response_data["links"][0].values()
        assert contact_info["email"] in response_data["contact_info"].values()
        assert response_data["private_site"] is None
