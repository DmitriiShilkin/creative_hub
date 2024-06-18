import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from constants.finance import Currency, PaymentPer
from constants.user_specialization import Grade
from models import Specialization, User, UserSpecialization
from models.user.mentorship import MentorshipDemand
from schemas.user.mentorship import MentorshipCreate
from services.user import mentorship


@pytest_asyncio.fixture
async def mentorship_fixture(
    async_session: AsyncSession,
    user_fixture: User,
    mentorship_demand_fixture: MentorshipDemand,
    user_specialization_fixture: UserSpecialization,
    specialization_fixture: Specialization,
) -> MentorshipDemand:
    create_data = MentorshipCreate(
        grades=[Grade.middle],
        is_show=True,
        is_paid=True,
        price=300,
        currency=Currency.euro,
        payment_per=PaymentPer.project,
        first_is_free=False,
        demands_ids=[mentorship_demand_fixture.id],
        keywords=[],
        descriptions=[{"description": "Менторшип", "lang": "ru"}],
        specialization_ids=[user_specialization_fixture.id],
    )
    user_mentorship = await mentorship.create_mentorship(
        db=async_session,
        create_data=create_data,
        user_id=user_fixture.id,
    )
    return user_mentorship
