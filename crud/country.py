from constants.crud_types import CreateSchemaType, UpdateSchemaType
from crud.async_crud import BaseAsyncCRUD
from models.country import Country


class CRUDCountry(BaseAsyncCRUD[Country, CreateSchemaType, UpdateSchemaType]):
    ...


crud_country = CRUDCountry(Country)
