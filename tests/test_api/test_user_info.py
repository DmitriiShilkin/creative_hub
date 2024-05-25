from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from models import Link, SocialNetwork, User, UserContact
from schemas.user.user_info import UserInfoCreateUpdate

ROOT_ENDPOINT = "/ch/v1/user/"


class TestUpdateUserInfo:
    async def test_create(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user: User,
        user_contact_info_fixture: UserContact,
    ) -> None:
        user_auth_headers = await get_auth_headers(user)
        link = {"name": "Test", "url": "https://example.com/"}
        network = {"network_name": "VK", "username": "test"}
        contact_info = {"email": "example@mail.ru", "phone_number": "12345677"}
        data = UserInfoCreateUpdate(
            links=[link], networks=[network], contact_info=contact_info
        )
        response = await http_client.put(
            ROOT_ENDPOINT, headers=user_auth_headers, json=data.model_dump()
        )
        assert response.status_code == 200
        response_data = response.json()
        assert link["name"] in response_data["links"][0].values()
        assert (
            network["network_name"]
            in response_data["social_networks"][0].values()
        )
        assert contact_info["email"] in response_data["contact_info"].values()

    async def test_update(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user: User,
        link_fixture: Link,
        social_network_fixture: SocialNetwork,
        user_contact_info_fixture: UserContact,
    ) -> None:
        user_auth_headers = await get_auth_headers(user)
        link = {
            "name": "Another Test",
            "url": "https://example.com/",
            "id": link_fixture.id,
        }
        network = {
            "network_name": "Facebook",
            "username": "test",
            "id": social_network_fixture.id,
        }
        contact_info = {"email": "example@mail.ru", "phone_number": "12345677"}
        data = UserInfoCreateUpdate(
            links=[link], networks=[network], contact_info=contact_info
        )
        response = await http_client.put(
            ROOT_ENDPOINT, headers=user_auth_headers, json=data.model_dump()
        )
        assert response.status_code == 200
        response_data = response.json()
        assert link["name"] in response_data["links"][0].values()
        assert (
            network["network_name"]
            in response_data["social_networks"][0].values()
        )
        assert contact_info["email"] in response_data["contact_info"].values()
