from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_multilingual.queries import select_i18n

from constants.crud_types import CreateSchemaType, UpdateSchemaType
from constants.i18n import Languages
from crud.async_crud import BaseAsyncCRUD
from models import Specialization


class CRUDSpecialization(
    BaseAsyncCRUD[Specialization, CreateSchemaType, UpdateSchemaType]
):
    async def get_multi_by_direction_id(
        self,
        db: AsyncSession,
        *,
        direction_id: int,
        skip: int = 0,
        limit: int = 1000,
        locale: Languages
    ) -> Sequence[Specialization]:
        statement = (
            select(self.model)
            .where(self.model.direction_id == direction_id)
            .offset(skip)
            .limit(limit)
        )
        stmt = select_i18n(
            stmt=statement, model=self.model, lang=locale, load_default=True
        )
        result = await db.execute(stmt)
        return result.scalars().unique().all()


crud_specialization = CRUDSpecialization(Specialization)
