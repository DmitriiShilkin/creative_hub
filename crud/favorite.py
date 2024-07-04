from typing import Dict, List, Optional

from sqlalchemy import and_, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, with_loader_criteria
from sqlalchemy.sql.selectable import Select

from constants.crud_types import CreateSchemaType
from crud.crud_mixins import BaseCRUD, CreateAsync, ReadAsync
from models import (
    City,
    Event,
    Favorite,
    Job,
    Organisation,
    Proposal,
    Specialization,
    User,
    View,
)
from schemas.crud.with_total import ObjectsWithTotalDataBaseDTO
from utilities.paginated_response import (
    get_paginated_dto,
    job_response_with_count,
)


class CRUDFavorite(
    BaseCRUD[Favorite],
    CreateAsync[Favorite, CreateSchemaType],
    ReadAsync[Favorite],
):
    async def get_organizations_by_user_id(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Organisation]:
        statement = (
            select(Organisation)
            .join(self.model, Organisation.id == self.model.organisation_id)
            .filter(
                self.model.user_id == user_id,
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_organizations_by_user_id_with_count(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> ObjectsWithTotalDataBaseDTO:
        statement = (
            select(
                Organisation,
                func.count(self.model.id).over().label("total_count"),
            )
            .join(self.model, Organisation.id == self.model.organisation_id)
            .filter(
                self.model.user_id == user_id,
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        objects = result.mappings().unique().all()
        return await get_paginated_dto(objects=objects, model=Organisation)

    async def get_favorite_users_by_user_id(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        statement = (
            select(User)
            .join(self.model, User.id == self.model.favorite_user_id)
            .filter(self.model.user_id == user_id)
            .options(joinedload(User.city).joinedload(City.country))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_favorite_users_by_user_id_with_count(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> ObjectsWithTotalDataBaseDTO:
        statement = (
            select(
                User,
                func.count(self.model.id).over().label("total_count"),
            )
            .join(self.model, User.id == self.model.favorite_user_id)
            .filter(self.model.user_id == user_id)
            .options(joinedload(User.city).joinedload(City.country))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        objects = result.mappings().unique().all()
        return await get_paginated_dto(objects=objects, model=User)

    async def get_events_by_user_id(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Event]:
        statement = (
            select(Event)
            .join(self.model, Event.id == self.model.event_id)
            .filter(
                self.model.user_id == user_id,
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_jobs_by_user_id_with_count(
        self,
        db: AsyncSession,
        user_id: int,
        current_user_ip: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Dict:
        subquery = await self._get_subquery_for_JobView(
            user_id, current_user_ip
        )
        statement = (
            select(
                Job,
                func.count(distinct(Proposal.id)).label("proposals_count"),
                func.count(distinct(View.id)).label("views"),
                (
                    func.count(distinct(Proposal.id)).label("proposals_count")
                    - func.coalesce(subquery.c.proposals_views, 0)
                ).label("new_proposals_count"),
                func.count(self.model.id).over().label("total_count"),
            )
            .join(self.model, Job.id == self.model.job_id)
            .filter(
                self.model.user_id == user_id,
            )
            .outerjoin(View, View.job_id == Job.id)
            .outerjoin(subquery, subquery.c.job_id == Job.id)
            .outerjoin(Job.proposals)
            .where(
                Job.is_draft.is_(False),
                Job.is_archived.is_(False),
            )
            .options(
                joinedload(Job.author),
                joinedload(Job.coauthors),
                joinedload(Job.contact_persons),
                joinedload(Job.city).joinedload(City.country),
                joinedload(Job.specializations).joinedload(
                    Specialization.direction
                ),
                joinedload(Job.proposals).load_only(Proposal.id),
                with_loader_criteria(
                    Job.proposals,
                    Proposal.user_id == user_id,
                ),
            )
            .group_by(self.model.id, Job.id, subquery.c.proposals_views)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        rows = result.unique().mappings().all()
        return await job_response_with_count(limit=limit, skip=skip, data=rows)

    async def _get_subquery_for_JobView(
        self,
        current_user_id: Optional[int] = None,
        current_user_ip: Optional[str] = None,
    ) -> Select:
        return (
            select(View.job_id, View.proposals_views).where(
                and_(
                    View.ip_address == current_user_ip,
                    View.user_id == current_user_id,
                ),
            )
        ).alias("filtered_job_view")


crud_favorite = CRUDFavorite(Favorite)
