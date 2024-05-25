from typing import List, Optional

from sqlalchemy import desc, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from crud.async_crud import BaseAsyncCRUD
from crud.crud_mixins import BulkAsync
from databases.queryset import QuerySet
from models.city import City
from models.user.education import Education
from schemas.user.education import (
    EducationCreateDB,
    EducationResponse,
    EducationUpdateDB,
)


class CRUDEducation(
    BaseAsyncCRUD[Education, EducationCreateDB, EducationResponse],
    BulkAsync[Education, EducationCreateDB, EducationUpdateDB],
):
    async def get_multi_by_user_id(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Education]:
        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .options(
                joinedload(self.model.city).joinedload(City.country),
                joinedload(self.model.certificates),
            )
            .order_by(
                desc(self.model.start_year), desc(self.model.start_month)
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.unique().scalars().all()

    async def get_multi_by_ids(
        self,
        db: AsyncSession,
        *,
        ids: List[int],
        skip: int = 0,
        limit: int = 100,
    ) -> QuerySet[Education]:
        query = (
            select(self.model)
            .where(self.model.id.in_(ids))
            .options(
                joinedload(self.model.city).joinedload(City.country),
                joinedload(self.model.certificates),
            )
            .order_by(
                desc(self.model.start_year), desc(self.model.start_month)
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        objects = result.unique().scalars().all()
        result = QuerySet(objects)
        result.model = self.model
        return result

    async def create(
        self,
        db: AsyncSession,
        *,
        create_schema: EducationCreateDB,
        commit: bool = True,
    ) -> Education:
        data = create_schema.model_dump(exclude_unset=True)
        stmt = (
            insert(self.model)
            .values(**data)
            .returning(self.model)
            .options(
                selectinload(self.model.certificates),
            )
        )
        res = await db.execute(stmt)
        obj = res.scalars().one()
        if commit:
            await db.commit()
        return obj

    async def create_bulk(
        self,
        db: AsyncSession,
        *,
        create_schemas: List[EducationCreateDB],
        commit: bool = True,
    ) -> List[Education]:
        data = [e.model_dump() for e in create_schemas]
        stmt = (
            insert(self.model)
            .values(data)
            .returning(self.model)
            .options(
                selectinload(self.model.certificates),
            )
        )
        res = await db.execute(stmt)
        obj = res.scalars().all()
        if commit:
            await db.commit()
        return obj

    async def get_by_id(
        self,
        db: AsyncSession,
        *,
        obj_id: int,
    ) -> Optional[Education]:
        statement = (
            select(self.model)
            .where(self.model.id == obj_id)
            .options(
                joinedload(self.model.user),
                joinedload(self.model.certificates),
                joinedload(self.model.city).joinedload(City.country),
            )
        )
        result = await db.execute(statement)
        return result.scalars().first()


crud_education = CRUDEducation(Education)
