import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from crud.user_profile_completeness import crud_profile_completeness
from models import ProfileCompleteness, User
from schemas.user.profile_completeness import ProfileCompletenessCreateDB


@pytest_asyncio.fixture
async def profile_completeness_fixture(
    async_session: AsyncSession, user_fixture: User
) -> ProfileCompleteness:
    schema = ProfileCompletenessCreateDB(
        main_percentage=60,
        contacts_percentage=90,
        education_percentage=100,
        experience_percentage=50,
        mentorship_percentage=0,
        user_id=user_fixture.id,
    )
    new_profile_completeness = await crud_profile_completeness.create(
        db=async_session, create_schema=schema
    )
    return new_profile_completeness
