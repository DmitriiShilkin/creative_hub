from pydantic import BaseModel


class CountryBase(BaseModel):
    name: str


class CountryCreateDB(CountryBase):
    pass


class CountryResponse(BaseModel):
    id: int
    name: str
