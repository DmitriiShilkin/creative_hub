from datetime import datetime, UTC
from typing import Dict, List, Optional

from sqlalchemy import and_, distinct, func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, with_loader_criteria, contains_eager
from sqlalchemy.sql.selectable import Select

from constants.i18n import Languages
from constants.crud_types import CreateSchemaType
from crud.crud_mixins import BaseCRUD, CreateAsync, ReadAsync
from models import (
    City,
    Event,
    EventView,
    Favorite,
    Job,
    JobView,
    Organisation,
    Proposal,
    Specialization,
    User,
    UserSpecialization,
)
from models.m2m import EventParticipants
from schemas.crud.with_total import ObjectsWithTotalDataBaseDTO
from utilities.paginated_response import get_paginated_dto, response_with_count


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

    async def get_events_by_user_id_with_count(
        self,
        db: AsyncSession,
        locale: Languages,
        user_id: int,
        current_user_ip: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Dict:
        subquery = await self._get_subquery_for_event_view(
            user_id, current_user_ip
        )
        statement = (
            select(
                Event,
                func.count(EventParticipants.user_id).label(
                    "participants_count"
                ),
                func.count(distinct(EventView.id)).label("views"),
                (
                    func.count(EventParticipants.user_id).label(
                        "participants_count"
                    )
                    - func.coalesce(subquery.c.participants_views, 0)
                ).label("new_participants_count"),
                func.count(self.model.id).over().label("total_count"),
            )
            .join(self.model, Event.id == self.model.event_id)
            .filter(
                self.model.user_id == user_id,
            )
            .outerjoin(EventView, EventView.event_id == Event.id)
            .outerjoin(
                EventParticipants, EventParticipants.event_id == self.model.id
            )
            .outerjoin(subquery, subquery.c.event_id == Event.id)
            .where(
                Event.is_draft.is_(False),
                Event.is_archived.is_(False),
                Event.end_datetime > datetime.now(tz=UTC),
            )
            .options(
                contains_eager(Event.event_views, alias=subquery),
                joinedload(Event.specializations),
                joinedload(Event.city).joinedload(City.country),
                joinedload(Event.timezone),
                joinedload(Event.organizers)
                .joinedload(User.specialization)
                .joinedload(UserSpecialization.specializations),
                joinedload(Event.speakers)
                .joinedload(User.specialization)
                .joinedload(UserSpecialization.specializations),
                joinedload(Event.creator),
                joinedload(Event.contact_persons),
                joinedload(Event.organisations).joinedload(
                    Organisation.private_sites
                ),
                joinedload(Event.participants),
                with_loader_criteria(
                    City.translation_model,
                    City.translation_model.locale == locale,
                ),
            )
            .group_by(
                self.model.id,
                Event.id,
                EventView.id,
                subquery.c.participants_views,
                subquery.c.event_id,
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        rows = result.unique().mappings().all()
        return await response_with_count(limit=limit, skip=skip, data=rows)

    async def get_jobs_by_user_id_with_count(
        self,
        db: AsyncSession,
        user_id: int,
        current_user_ip: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Dict:
        subquery = await self._get_subquery_for_job_view(
            user_id, current_user_ip
        )
        statement = (
            select(
                Job,
                func.count(distinct(Proposal.id)).label("proposals_count"),
                func.count(distinct(JobView.id)).label("views"),
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
            .outerjoin(JobView, JobView.job_id == Job.id)
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
        return await response_with_count(limit=limit, skip=skip, data=rows)

    async def _get_subquery_for_job_view(
        self,
        current_user_id: Optional[int] = None,
        current_user_ip: Optional[str] = None,
    ) -> Select:
        return (
            select(JobView.job_id, JobView.proposals_views).where(
                and_(
                    JobView.ip_address == current_user_ip,
                    JobView.user_id == current_user_id,
                ),
            )
        ).alias("filtered_job_view")

    async def _get_subquery_for_event_view(
        self,
        current_user_id: Optional[int] = None,
        current_user_ip: Optional[str] = None,
    ) -> Select:
        return (
            select(EventView.event_id, EventView.participants_views).where(
                or_(
                    EventView.user_id == current_user_id,
                    and_(
                        EventView.user_id.is_(None),
                        EventView.ip_address == current_user_ip,
                    ),
                )
            )
        ).alias("filtered_event_view")


crud_favorite = CRUDFavorite(Favorite)
