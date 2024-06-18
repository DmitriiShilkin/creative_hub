import uuid
from typing import Callable

from httpx import AsyncClient

from constants.finance import Currency, PaymentPer
from constants.user_specialization import Grade
from models import Specialization
from models.keyword import Keyword
from models.user.mentorship import MentorshipDemand
from models.user.user import User
from models.user.user_specialization import UserSpecialization
from schemas.user.mentorship import (
    MentorshipCreate,
    MentorshipResponse,
    MentorshipUpdate,
)

ROOT_ENDPOINT = "/ch/v1/mentorship/"


class TestMentorship:
    async def test_create_mentorship(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        user_fixture_2: User,
        get_auth_headers: Callable,
        user_specialization_fixture: UserSpecialization,
        mentorship_demand_fixture: MentorshipDemand,
        specialization_fixture: Specialization,
    ) -> None:
        auth_headers = await get_auth_headers(user_fixture)
        mentorship_data = MentorshipCreate(
            grades=[Grade.middle],
            is_show=True,
            is_paid=True,
            price=300,
            currency=Currency.dollar,
            payment_per=PaymentPer.project,
            first_is_free=False,
            demands_ids=[
                mentorship_demand_fixture.id,
            ],
            specialization_ids=[
                user_specialization_fixture.id,
            ],
            keywords=[],
            descriptions=[{"description": "Менторшип", "lang": "ru"}],
        )
        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=auth_headers,
            json=mentorship_data.model_dump(),
        )
        assert response.status_code == 200

        response_data = response.json()
        assert Grade.middle in response_data["grades"]

    async def test_create_mentorship_404(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        get_auth_headers: Callable,
        user_specialization_fixture: UserSpecialization,
        specialization_fixture: Specialization,
    ) -> None:
        # If some objects not found, returns 404
        auth_headers = await get_auth_headers(user_fixture)
        mentorship_data = MentorshipCreate(
            grades=[Grade.middle],
            is_show=True,
            is_paid=True,
            price=300,
            currency=Currency.dollar,
            payment_per=PaymentPer.project,
            first_is_free=False,
            demands_ids=[2],
            keywords=[],
            specialization_ids=[user_specialization_fixture.id],
            descriptions=[{"description": "Менторшип", "lang": "ru"}],
        )
        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=auth_headers,
            json=mentorship_data.model_dump(),
        )
        assert response.status_code == 404

        response_data = response.json()
        err_message = (
            f"MentorshipDemand with `{mentorship_data.demands_ids[0]}` "
            "ids not found!"
        )
        assert response_data["detail"] == err_message

    async def test_read_mentorship(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        mentorship_fixture: MentorshipResponse,
    ) -> None:
        endpoint = f"{ROOT_ENDPOINT}{user_fixture.uid}/"
        response = await http_client.get(endpoint)
        assert response.status_code == 200

        response_data = response.json()
        assert Grade.middle in response_data["grades"]

        # If user not found, returns 404
        random_user_uid = uuid.uuid4()
        endpoint = f"{ROOT_ENDPOINT}{random_user_uid}/"
        response = await http_client.get(endpoint)
        assert response.status_code == 404

        err_message = f"User {random_user_uid} not found."
        response_data = response.json()
        assert response_data["detail"] == err_message

    async def test_read_mentorship_404(
        self,
        http_client: AsyncClient,
        user_fixture: User,
    ) -> None:
        endpoint = f"{ROOT_ENDPOINT}{user_fixture.uid}/"
        response = await http_client.get(endpoint)
        assert response.status_code == 404

        err_message = "User mentorship not found."
        response_data = response.json()
        assert response_data["detail"] == err_message

    async def test_update_mentorship(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        get_auth_headers: Callable,
        user_specialization_fixture: UserSpecialization,
        mentorship_demand_fixture: MentorshipDemand,
        mentorship_fixture: MentorshipResponse,
        keyword_fixture: Keyword,
    ) -> None:
        auth_headers = await get_auth_headers(user_fixture)

        # If some objects not found, returns 404
        update_data = MentorshipUpdate(
            grades=[Grade.intern],
            is_show=True,
            is_paid=False,
            price=9000,
            currency=Currency.yuan,
            payment_per=PaymentPer.hour,
            first_is_free=True,
            demands_ids=[2],
            keywords=[{"name": "Design"}],
            specialization_ids=[user_specialization_fixture.id],
            descriptions=[{"description": "Менторшип", "lang": "ru"}],
        )
        response = await http_client.put(
            ROOT_ENDPOINT,
            headers=auth_headers,
            json=update_data.model_dump(),
        )
        assert response.status_code == 404

        response_data = response.json()
        err_message = (
            f"MentorshipDemand with `{update_data.demands_ids[0]}` "
            "ids not found!"
        )
        assert response_data["detail"] == err_message

        update_data = MentorshipUpdate(
            grades=[Grade.lead],
            is_show=True,
            is_paid=False,
            price=9000,
            currency=Currency.yuan,
            payment_per=PaymentPer.hour,
            first_is_free=True,
            demands_ids=[mentorship_demand_fixture.id],
            keywords=[{"name": "Design"}],
            specialization_ids=[user_specialization_fixture.id],
            descriptions=[{"description": "Менторшип", "lang": "ru"}],
        )
        response = await http_client.put(
            ROOT_ENDPOINT,
            headers=auth_headers,
            json=update_data.model_dump(),
        )
        assert response.status_code == 200

        response_data = response.json()
        assert Grade.lead in response_data["grades"]

    # If mentorship not found, returns 404
    async def test_update_mentorship_404(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        get_auth_headers: Callable,
        user_specialization_fixture: UserSpecialization,
        mentorship_demand_fixture: MentorshipDemand,
        keyword_fixture: Keyword,
    ) -> None:
        auth_headers = await get_auth_headers(user_fixture)
        update_data = MentorshipUpdate(
            grades=[Grade.lead],
            is_show=True,
            is_paid=False,
            price=9000,
            currency=Currency.yuan,
            payment_per=PaymentPer.hour,
            first_is_free=True,
            demands_ids=[mentorship_demand_fixture.id],
            keywords=[{"name": "Design"}],
            specialization_ids=[user_specialization_fixture.id],
            descriptions=[{"description": "Менторшип", "lang": "ru"}],
        )
        response = await http_client.put(
            ROOT_ENDPOINT,
            headers=auth_headers,
            json=update_data.model_dump(),
        )
        assert response.status_code == 404

        response_data = response.json()
        err_message = "User mentorship not found."
        assert response_data["detail"] == err_message
