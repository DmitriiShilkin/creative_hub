import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from crud.favorite import crud_favorite
from models import Organisation, User
from schemas.user.favorite import FavoriteBase


@pytest_asyncio.fixture
async def organisation_favorites_list_fixture(
    async_session: AsyncSession,
    user_fixture: User,
    organisation_fixture: Organisation,
):
    schema = FavoriteBase(
        user_id=user_fixture.id,
        favorite_user_id=None,
        organisation_id=organisation_fixture.id,
        event_id=None,
        job_id=None,
    )
    await crud_favorite.create(db=async_session, create_schema=schema)
    favorite_organizations = await crud_favorite.get_organizations_by_user_id(
        db=async_session, user_id=user_fixture.id
    )
    return favorite_organizations
