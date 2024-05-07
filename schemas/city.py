from pydantic import BaseModel

from schemas.country import CountryResponse


class CityBase(BaseModel):
    name: str


class CityCreateDB(CityBase):
    country_id: int


class CityResponse(BaseModel):
    id: int
    name: str


class CityWithCountryResponse(BaseModel):
    id: int
    name: str
    country: CountryResponse
