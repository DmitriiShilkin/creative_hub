from constants.crud_types import CreateSchemaType, UpdateSchemaType
from crud.async_crud import BaseAsyncCRUD
from models import Direction


class CRUDDirection(
    BaseAsyncCRUD[Direction, CreateSchemaType, UpdateSchemaType]
):
    ...


crud_direction = CRUDDirection(Direction)
