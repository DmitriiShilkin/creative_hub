from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from constants.crud_types import CreateSchemaType, UpdateSchemaType
from crud.async_crud import BaseAsyncCRUD
from models import FavoriteUsers, User


class CRUDFavoriteUsers(
    BaseAsyncCRUD[FavoriteUsers, CreateSchemaType, UpdateSchemaType]
):
    async def get_multi_by_user_id(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ):
        statement = (
            select(User)
            .select_from(self.model)
            .where(
                self.model.user_id == user_id,
                User.id == self.model.favorite_user_id,
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()


crud_favorite_user = CRUDFavoriteUsers(FavoriteUsers)
