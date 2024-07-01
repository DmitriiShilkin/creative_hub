from typing import Dict, Optional

from sqlalchemy import and_, desc, distinct, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, joinedload, with_loader_criteria
from sqlalchemy.sql.selectable import Select

from api.filters.job import JobFilter
from crud.async_crud import BaseAsyncCRUD
from databases.queryset import QuerySet
from models import City, Country, Job, Proposal, Specialization, View
from models.m2m import JobSpecializations
from schemas.crud.job import JobDataBaseDTO
from schemas.frilance.job import JobCreateDB, JobUpdate
from utilities.paginated_response import job_response_with_count


class CRUDJobWithCounters(BaseAsyncCRUD[Job, JobCreateDB, JobUpdate]):
    async def get_by_id(
        self,
        db: AsyncSession,
        *,
        obj_id: int,
        author_id: Optional[int] = None,
        current_user_ip: Optional[str] = None,
    ) -> Optional[JobDataBaseDTO]:
        subquery = await self._get_subquery_for_JobView(
            author_id, current_user_ip
        )
        all_job_views = aliased(View)
        statement = (
            select(
                self.model,
                func.count(distinct(Proposal.id)).label("proposals_count"),
                func.count(distinct(all_job_views.id)).label("views"),
                (
                    func.count(distinct(Proposal.id)).label("proposals_count")
                    - func.coalesce(subquery.c.proposals_views, 0)
                ).label("new_proposals_count"),
            )
            .outerjoin(all_job_views, all_job_views.job_id == self.model.id)
            .outerjoin(subquery, subquery.c.job_id == self.model.id)
            .outerjoin(self.model.proposals)
            .where(self.model.id == obj_id)
            .options(
                joinedload(self.model.author),
                joinedload(self.model.coauthors),
                joinedload(self.model.files),
                joinedload(self.model.specializations).joinedload(
                    Specialization.direction
                ),
                joinedload(self.model.contact_persons),
                joinedload(self.model.proposal_table_config),
                joinedload(self.model.view_records),
                joinedload(self.model.city).joinedload(City.country),
                joinedload(self.model.proposals).options(
                    joinedload(Proposal.user),
                    joinedload(Proposal.files),
                ),
                with_loader_criteria(
                    self.model.proposals,
                    Proposal.user_id == author_id,
                ),
            )
            .group_by(self.model.id, subquery.c.proposals_views)
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
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        author_id: Optional[int] = None,
        current_user_id: Optional[int] = None,
        current_user_ip: Optional[str] = None,
        filters: Optional[JobFilter] = None,
    ) -> Dict:
        subquery = await self._get_subquery_for_JobView(
            current_user_id, current_user_ip
        )
        all_job_views = aliased(View)
        statement = (
            select(
                self.model,
                func.count(distinct(Proposal.id)).label("proposals_count"),
                func.count(distinct(all_job_views.id)).label("views"),
                (
                    func.count(distinct(Proposal.id)).label("proposals_count")
                    - func.coalesce(subquery.c.proposals_views, 0)
                ).label("new_proposals_count"),
                func.count(self.model.id).over().label("total_count"),
                exists(subquery.c.job_id).label("is_viewed_by_current_user"),
            )
            .outerjoin(all_job_views, all_job_views.job_id == self.model.id)
            .outerjoin(subquery, subquery.c.job_id == self.model.id)
            .outerjoin(self.model.proposals)
            .outerjoin(City, City.id == self.model.city_id)
            .outerjoin(Country, City.country_id == Country.id)
            .outerjoin(
                JobSpecializations, JobSpecializations.job_id == self.model.id
            )
            .outerjoin(
                Specialization,
                JobSpecializations.specialization_id == Specialization.id,
            )
            .where(
                self.model.is_draft.is_(False),
                self.model.is_archived.is_(False),
            )
            .options(
                joinedload(self.model.author),
                joinedload(self.model.coauthors),
                joinedload(self.model.contact_persons),
                joinedload(self.model.city).joinedload(City.country),
                joinedload(self.model.specializations).joinedload(
                    Specialization.direction
                ),
                joinedload(self.model.proposals).load_only(Proposal.id),
                with_loader_criteria(
                    self.model.proposals,
                    Proposal.user_id == current_user_id,
                ),
            )
            .order_by(desc(self.model.created_at))
            .group_by(self.model.id, subquery.c.proposals_views)
            .offset(skip)
            .limit(limit)
        )
        if author_id:
            statement = statement.where(self.model.author_id == author_id)
        if filters:
            if filters.accepted_languages__in:
                statement = statement.filter(
                    self.model.accepted_languages.overlap(
                        filters.accepted_languages__in
                    )
                )
                filters.accepted_languages__in = None
            statement = filters.filter(statement)
        result = await db.execute(statement)
        rows = result.unique().mappings().all()
        return await job_response_with_count(limit, skip, rows)

    async def get_multi_by_ids(
        self,
        db: AsyncSession,
        *,
        ids: list[int],
        current_user_id: Optional[int] = None,
        current_user_ip: Optional[str] = None,
    ) -> list[JobDataBaseDTO]:
        if not ids:
            return []
        subquery = await self._get_subquery_for_JobView(
            current_user_id, current_user_ip
        )
        statement = (
            select(
                self.model,
                func.count(distinct(Proposal.id)).label("proposals_count"),
                (
                    func.count(distinct(Proposal.id)).label("proposals_count")
                    - func.coalesce(subquery.c.proposals_views, 0)
                ).label("new_proposals_count"),
            )
            .outerjoin(subquery, subquery.c.job_id == self.model.id)
            .outerjoin(self.model.proposals)
            .where(self.model.id.in_(ids))
            .options(
                joinedload(self.model.view_records),
            )
            .group_by(self.model.id, subquery.c.proposals_views)
        )
        result = await db.execute(statement)
        objects = result.mappings().unique().all()
        result = QuerySet(objects)
        result.model = self.model
        return result

    async def get_multi_jobs_for_author(
        self,
        db: AsyncSession,
        author_id: int,
        filters: Optional[JobFilter] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Dict:
        subquery = await self._get_subquery_for_JobView(
            current_user_id=author_id
        )
        all_job_views = aliased(View)
        statement = (
            select(
                self.model,
                func.count(distinct(Proposal.id)).label("proposals_count"),
                func.count(distinct(all_job_views.id)).label("views"),
                (
                    func.count(distinct(Proposal.id)).label("proposals_count")
                    - func.coalesce(subquery.c.proposals_views, 0)
                ).label("new_proposals_count"),
                func.count(self.model.id).over().label("total_count"),
            )
            .outerjoin(all_job_views, all_job_views.job_id == self.model.id)
            .outerjoin(subquery, subquery.c.job_id == self.model.id)
            .outerjoin(self.model.proposals)
            .outerjoin(City, City.id == self.model.city_id)
            .outerjoin(Country, City.country_id == Country.id)
            .outerjoin(
                JobSpecializations, JobSpecializations.job_id == self.model.id
            )
            .outerjoin(
                Specialization,
                JobSpecializations.specialization_id == Specialization.id,
            )
            .where(self.model.author_id == author_id)
            .options(
                joinedload(self.model.author),
                joinedload(self.model.coauthors),
                joinedload(self.model.contact_persons),
                joinedload(self.model.files),
                joinedload(self.model.city).joinedload(City.country),
                joinedload(self.model.specializations).joinedload(
                    Specialization.direction
                ),
            )
            .order_by(desc(self.model.created_at))
            .group_by(self.model.id, subquery.c.proposals_views)
            .offset(skip)
            .limit(limit)
        )

        if filters is not None:
            if filters.accepted_languages__in:
                statement = statement.filter(
                    self.model.accepted_languages.overlap(
                        filters.accepted_languages__in
                    )
                )
                filters.accepted_languages__in = None
            statement = filters.filter(statement)

        result = await db.execute(statement)
        rows = result.unique().mappings().all()
        return await job_response_with_count(limit, skip, rows)

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


crud_job = CRUDJobWithCounters(Job)
