from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_multilingual.queries import select_i18n

from api.filters.keyword import KeywordSearch
from constants.crud_types import CreateSchemaType, UpdateSchemaType
from constants.i18n import Languages
from crud.async_crud import BaseAsyncCRUD
from models.keyword import Keyword


class CRUDKeyword(BaseAsyncCRUD[Keyword, CreateSchemaType, UpdateSchemaType]):
    async def get_multi(
        self,
        filters: Optional[KeywordSearch],
        db: AsyncSession,
        locale: Languages,
        skip: int = 0,
        limit: int = 1000,
    ):
        statement = select(self.model).offset(skip).limit(limit)
        stmt = select_i18n(
            stmt=statement, model=self.model, lang=locale, load_default=True
        )
        statement = filters.filter(stmt)
        result = await db.execute(statement)
        return result.scalars().unique().all()


crud_keyword = CRUDKeyword(Keyword)
