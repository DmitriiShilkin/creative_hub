import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from constants.user_specialization import Grade, Status
from crud.user_specialization import crud_user_specialization
from models.user.user import User
from models.user.user_specialization import UserSpecialization
from schemas.user.user_specialization import UserSpecializationCreateDB


@pytest_asyncio.fixture
async def user_specialization_fixture(
    async_session: AsyncSession,
    user_fixture: User,
) -> UserSpecialization:
    create_schema = UserSpecializationCreateDB(
        grade=Grade.middle,
        status=Status.considering_offers,
        is_ready_to_move=False,
        is_ready_for_remote_work=False,
        user_id=user_fixture.id,
    )
    new_user_specialization = await crud_user_specialization.create(
        db=async_session,
        create_schema=create_schema,
    )
    return new_user_specialization
