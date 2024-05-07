import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from crud.city import crud_city
from models import City, Country
from schemas.city import CityCreateDB


@pytest_asyncio.fixture
async def city(async_session: AsyncSession, country: Country) -> City:
    schema = CityCreateDB(
        name="Test city name",
        country_id=country.id,
    )
    new_city = await crud_city.create(db=async_session, create_schema=schema)
    return new_city
