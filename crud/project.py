from pydantic import BaseModel
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from constants.crud_types import ModelType, UpdateSchemaType
from crud.async_crud import BaseAsyncCRUD
from models.project import Project
from schemas.project import ProjectCreate


class CRUDProject(BaseAsyncCRUD[Project, ProjectCreate, UpdateSchemaType]):
    async def get_multi_by_user_id(
        self,
        db: AsyncSession,
        *,
        author_id: int,
        skip: int = 0,
        limit: int = 100,
    ):
        statement = (
            select(self.model)
            .options(
                joinedload(self.model.author),
                joinedload(self.model.coauthors),
                joinedload(self.model.keywords),
            )
            .where(self.model.author_id == author_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.unique().scalars().all()

    async def get_by_id(self, db: AsyncSession, *, project_id: int):
        statement = (
            select(self.model)
            .where(self.model.id == project_id)
            .options(
                joinedload(self.model.author),
                joinedload(self.model.keywords),
                joinedload(self.model.coauthors),
            )
        )
        result = await db.execute(statement)
        return result.scalars().first()

    async def create(
        self,
        db: AsyncSession,
        *,
        create_schema: ProjectCreate,
        commit: bool = True,
    ):
        data = create_schema.model_dump(exclude_unset=True)
        stmt = (
            insert(self.model)
            .values(**data)
            .returning(self.model)
            .options(
                selectinload(self.model.coauthors),
                selectinload(self.model.keywords),
            )
        )
        res = await db.execute(stmt)
        if commit:
            await db.commit()
        return res.scalars().first()

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        update_data: ProjectCreate,
        commit: bool = True,
    ):
        if isinstance(update_data, BaseModel):
            update_data = update_data.model_dump(exclude_unset=True)
        if not update_data:
            return db_obj
        stmt = (
            update(self.model)
            .values(**update_data)
            .where(self.model.id == db_obj.id)
            .options(
                joinedload(self.model.coauthors),
                joinedload(self.model.keywords),
            )
            .returning(self.model)
        )
        res = await db.execute(stmt)
        if commit:
            await db.commit()
        return res.scalars().first()


crud_project = CRUDProject(Project)
