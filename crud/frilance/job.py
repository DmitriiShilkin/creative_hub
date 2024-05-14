from typing import Optional

from sqlalchemy import and_, func, insert, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from api.filters.job import JobFilter
from crud.async_crud import BaseAsyncCRUD
from models import Job, Specialization
from schemas.frilance.job import JobCreateDB, JobUpdate


class CRUDJob(BaseAsyncCRUD[Job, JobCreateDB, JobUpdate]):
    async def get_by_id(
        self, db: AsyncSession, *, obj_id: int, author_id: Optional[int] = None
    ) -> Optional[Job]:
        statement = (
            select(
                self.model,
                func.count(self.model.proposals).label("proposals_count"),
            )
            .outerjoin(self.model.proposals)
            .where(self.model.id == obj_id)
            .options(
                joinedload(self.model.author),
                joinedload(self.model.files),
                joinedload(self.model.specializations).joinedload(
                    Specialization.direction
                ),
                joinedload(self.model.contact_persons),
                joinedload(self.model.proposal_table_config),
            )
            .group_by(self.model.id)
        )
        if author_id is not None:
            statement = statement.where(
                or_(
                    self.model.is_draft.is_(False),
                    and_(
                        self.model.is_draft.is_(True),
                        self.model.author_id == author_id,
                    ),
                )
            )
        else:
            statement = statement.where(self.model.is_draft.is_(False))
        result = await db.execute(statement)
        return result.mappings().first()

    async def get_multi(
        self, db: AsyncSession, skip: int = 0, limit: int = 100, filters=None
    ):
        statement = (
            select(
                self.model,
                func.count(self.model.proposals).label("proposals_count"),
            )
            .outerjoin(self.model.proposals)
            .offset(skip)
            .limit(limit)
            .options(
                joinedload(self.model.author),
                joinedload(self.model.contact_persons),
                joinedload(self.model.specializations).joinedload(
                    Specialization.direction
                ),
            )
            .group_by(self.model.id)
        )
        result = await db.execute(statement)
        return result.unique().mappings().all()

    async def get_multi_by_author_id(
        self,
        db: AsyncSession,
        author_id: int,
        skip: int = 0,
        limit: int = 100,
        is_draft: bool = False,
        filters: Optional[JobFilter] = None,
    ):
        statement = (
            select(
                self.model,
                func.count(self.model.proposals).label("proposals_count"),
            )
            .outerjoin(self.model.proposals)
            .where(self.model.author_id == author_id)
            .offset(skip)
            .limit(limit)
            .options(
                joinedload(self.model.author),
                joinedload(self.model.contact_persons),
                joinedload(self.model.specializations).joinedload(
                    Specialization.direction
                ),
            )
            .group_by(self.model.id)
        )

        if is_draft is True:
            statement = statement.where(self.model.author_id == author_id)
            statement = filters.filter(statement)
        elif is_draft is False:
            statement = statement.where(self.model.is_draft == is_draft)

        if filters is not None:
            statement = filters.filter(statement)

        result = await db.execute(statement)
        return result.unique().mappings().all()

    async def create(
        self,
        db: AsyncSession,
        *,
        create_schema: JobCreateDB,
        commit: bool = True,
    ) -> Job:
        data = create_schema.model_dump(exclude_unset=True)
        stmt = (
            insert(self.model)
            .values(**data)
            .returning(self.model)
            .options(
                selectinload(self.model.specializations),
                selectinload(self.model.files),
            )
        )
        res = await db.execute(stmt)
        obj = res.scalars().one()
        if commit:
            await db.commit()
        return obj


crud_job = CRUDJob(Job)
