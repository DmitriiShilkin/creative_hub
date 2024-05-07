import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from constants.month import Month
from crud.user_experience import crud_user_experience
from models import City, User, UserExperience
from schemas.user.user_experience import ExperienceCreateDB


@pytest_asyncio.fixture
async def user_experience(
    async_session: AsyncSession, user: User, city: City
) -> UserExperience:
    schema = ExperienceCreateDB(
        company_name="Test company name",
        job_title="Test job title",
        start_month=Month.February,
        start_year=2024,
        still_working=True,
        city_id=city.id,
        user_id=user.id,
    )
    new_user_experience = await crud_user_experience.create(
        db=async_session, create_schema=schema
    )
    return new_user_experience
