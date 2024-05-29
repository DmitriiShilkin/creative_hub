import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from crud.private_site import crud_private_site
from models import PrivateSite, User
from schemas.private_site import PrivateSiteCreateDB


@pytest_asyncio.fixture
async def private_site_fixture(
    async_session: AsyncSession, user_fixture: User
) -> PrivateSite:
    schema = PrivateSiteCreateDB(
        name="Test name",
        url="https://test_private_site.com/",
        user_id=user_fixture.id,
    )
    new_private_site = await crud_private_site.create(
        db=async_session, create_schema=schema
    )
    return new_private_site
