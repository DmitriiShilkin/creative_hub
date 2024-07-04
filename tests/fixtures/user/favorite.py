from typing import List

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from crud.favorite import crud_favorite
from models import User
from schemas.user.favorite import FavoriteBase
from schemas.user.user import UserSimpleResponse


@pytest_asyncio.fixture
async def user_favorites_list_fixture(
    async_session: AsyncSession, user_fixture: User, user_fixture_2: User
) -> List[UserSimpleResponse]:
    schema = FavoriteBase(
        user_id=user_fixture.id,
        favorite_user_id=user_fixture_2.id,
        organisation_id=None,
        event_id=None,
        job_id=None,
    )
    await crud_favorite.create(db=async_session, create_schema=schema)
    favorite_users = await crud_favorite.get_favorite_users_by_user_id(
        db=async_session, user_id=user_fixture.id
    )
    return favorite_users
