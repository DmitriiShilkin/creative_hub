import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from crud.favorite import crud_favorite
from models import Event, User
from schemas.user.favorite import FavoriteBase


@pytest_asyncio.fixture
async def event_favorites_list_fixture(
    async_session: AsyncSession,
    user_fixture: User,
    event_fixture: Event,
):
    schema = FavoriteBase(
        user_id=user_fixture.id,
        favorite_user_id=None,
        organisation_id=None,
        event_id=event_fixture.id,
        job_id=None,
    )
    await crud_favorite.create(db=async_session, create_schema=schema)
    return await crud_favorite.get_events_by_user_id(
        db=async_session, user_id=user_fixture.id
    )
