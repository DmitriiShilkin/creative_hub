from typing import Generic, Optional, Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy_multilingual.queries import select_i18n

from constants.crud_types import ModelType
from constants.i18n import Languages
from databases.queryset import QuerySet


class ReadAsync(Generic[ModelType]):
    async def get(self, db: AsyncSession, obj_id: int) -> Optional[ModelType]:
        return await db.get(self.model, obj_id)

    async def get_by_id(
        self, db: AsyncSession, *, obj_id: int
    ) -> Optional[ModelType]:
        statement = select(self.model).where(self.model.id == obj_id)
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_by_uid(
        self, db: AsyncSession, *, uid: UUID
    ) -> Optional[ModelType]:
        statement = select(self.model).where(self.model.uid == uid)
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, skip: int = 0, limit: int = 1000, filters=None
    ) -> Sequence[ModelType]:
        statement = select(self.model).offset(skip).limit(limit)
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_multi_lang(
        self,
        db: AsyncSession,
        locale: Languages,
        skip: int = 0,
        limit: int = 1000,
    ) -> Sequence[ModelType]:
        statement = select(self.model).offset(skip).limit(limit)
        stmt = select_i18n(
            stmt=statement, model=self.model, lang=locale, load_default=True
        )
        result = await db.execute(stmt)
        return result.scalars().unique().all()

    async def get_multi_by_uids(
        self, db: AsyncSession, *, uids: list[UUID]
    ) -> Sequence[ModelType]:
        if not uids:
            return []
        statement = select(self.model).where(self.model.uid.in_(uids))
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_multi_by_ids(
        self, db: AsyncSession, *, ids: list[int]
    ) -> Sequence[ModelType]:
        if not ids:
            return []
        statement = select(self.model).where(self.model.id.in_(ids))
        result = await db.execute(statement)
        objects = result.scalars().all()
        result = QuerySet(objects)
        result.model = self.model
        return result
