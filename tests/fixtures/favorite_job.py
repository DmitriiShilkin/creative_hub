import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from crud.favorite import crud_favorite
from models import Job, User
from schemas.user.favorite import FavoriteBase


@pytest_asyncio.fixture
async def job_favorites_list_fixture(
    async_session: AsyncSession,
    user_fixture: User,
    job_fixture: Job,
):
    schema = FavoriteBase(
        user_id=user_fixture.id,
        favorite_user_id=None,
        organisation_id=None,
        event_id=None,
        job_id=job_fixture.id,
    )
    await crud_favorite.create(db=async_session, create_schema=schema)
    return await crud_favorite.get_jobs_by_user_id_with_count(
        db=async_session, user_id=user_fixture.id
    )
