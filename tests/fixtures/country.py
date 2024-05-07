import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from crud.country import crud_country
from models import Country
from schemas.country import CountryCreateDB


@pytest_asyncio.fixture
async def country(async_session: AsyncSession) -> Country:
    schema = CountryCreateDB(
        name="Test country name",
    )
    new_country = await crud_country.create(
        db=async_session, create_schema=schema
    )
    return new_country
