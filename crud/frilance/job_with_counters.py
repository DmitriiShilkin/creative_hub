from typing import Dict, Optional, Union

from sqlalchemy import (
    Subquery,
    and_,
    case,
    desc,
    distinct,
    func,
    nullslast,
    or_,
    select,
    literal,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    aliased,
    joinedload,
    with_loader_criteria,
    selectinload,
)
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.selectable import Select

from api.filters.job import JobFilter
from constants.sorting import SortOrder
from crud.crud_mixins import BaseCRUD, ReadAsync
from databases.queryset import QuerySet
from models import City, Country, Favorite, Job, Proposal, Specialization
from models.frilance import JobView
from models.m2m import JobSpecializations
from models.user import User
from schemas.crud.job import JobDataBaseDTO
from utilities.paginated_response import response_with_count


class CRUDJobWithCounters(BaseCRUD[Job], ReadAsync[Job]):
    async def get_by_id(
        self,
        db: AsyncSession,
        *,
        obj_id: int,
        author_id: Optional[int] = None,
        current_user_ip: Optional[str] = None,
    ) -> Optional[Dict]:
        subquery = await self._get_subquery_for_job_view(
            obj_id=obj_id,
            current_user_id=author_id,
            current_user_ip=current_user_ip,
        )
        favorite_subquery = await self._get_subquery_for_favorite_job(
            job_id=obj_id,
            current_user_id=author_id,
        )
        proposal_subquery = await self._get_subquery_for_job_proposal(
            job_id=self.model.id, current_user_id=author_id
        )

        all_job_views = aliased(JobView)

        statement = (
            select(
                self.model,
                func.count(distinct(Proposal.id)).label("proposals_count"),
                func.count(distinct(all_job_views.id)).label("views"),
                (
                    func.count(distinct(Proposal.id)).label("proposals_count")
                    - func.coalesce(subquery.c.proposals_views, 0)
                ).label("new_proposals_count"),
                func.bool_or(subquery.c.existing_view).label("existing_view"),
                favorite_subquery.c.is_favorite.label("is_favorite"),
                proposal_subquery.c.is_applied.label("is_applied"),
            )
            .outerjoin(all_job_views, all_job_views.job_id == self.model.id)
            .outerjoin(subquery, subquery.c.job_id == self.model.id)
            .outerjoin(
                favorite_subquery, favorite_subquery.c.job_id == self.model.id
            )
            .outerjoin(
                proposal_subquery, proposal_subquery.c.job_id == self.model.id
            )
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
                joinedload(self.model.job_views),
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
            .group_by(
                self.model.id,
                subquery.c.job_id,
                subquery.c.proposals_views,
                favorite_subquery.c.is_favorite,
                proposal_subquery.c.is_applied,
            )
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
        favorite: bool,
        skip: int = 0,
        limit: int = 20,
        author_id: Optional[int] = None,
        current_user_id: Optional[int] = None,
        current_user_ip: Optional[str] = None,
        filters: Optional[JobFilter] = None,
        sort_by: Optional[str] = None,
        sort_order: SortOrder = SortOrder.asc,
    ) -> Dict:
        subquery = await self._get_subquery_for_job_view(
            obj_id=self.model.id,
            current_user_id=current_user_id,
            current_user_ip=current_user_ip,
        )
        favorite_subquery = await self._get_subquery_for_favorite_job(
            job_id=self.model.id,
            current_user_id=current_user_id,
        )
        proposal_subquery = await self._get_subquery_for_job_proposal(
            job_id=self.model.id, current_user_id=current_user_id
        )
        all_job_views = aliased(JobView)
        statement = (
            select(
                self.model,
                func.count(distinct(Proposal.id)).label("proposals_count"),
                func.count(distinct(all_job_views.id)).label("views"),
                (
                    func.count(distinct(Proposal.id)).label("proposals_count")
                    - func.coalesce(subquery.c.proposals_views, 0)
                ).label("new_proposals_count"),
                func.bool_or(subquery.c.existing_view).label("existing_view"),
                func.count(self.model.id).over().label("total_count"),
                favorite_subquery.c.is_favorite.label("is_favorite"),
                proposal_subquery.c.is_applied.label("is_applied"),
            )
            .outerjoin(all_job_views, all_job_views.job_id == self.model.id)
            .outerjoin(subquery, subquery.c.job_id == self.model.id)
            .outerjoin(
                favorite_subquery, favorite_subquery.c.job_id == self.model.id
            )
            .outerjoin(
                proposal_subquery, proposal_subquery.c.job_id == self.model.id
            )
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
            .outerjoin(User, User.id == self.model.author_id)
            .where(
                self.model.is_draft.is_(False),
                self.model.is_archived.is_(False),
            )
            .options(
                selectinload(self.model.author),
                selectinload(self.model.coauthors),
                selectinload(self.model.contact_persons),
                selectinload(self.model.city).selectinload(City.country),
                selectinload(self.model.specializations).joinedload(
                    Specialization.direction
                ),
                selectinload(self.model.proposals).load_only(Proposal.id),
                with_loader_criteria(
                    self.model.proposals,
                    Proposal.user_id == current_user_id,
                ),
            )
            .order_by(desc(self.model.created_at))
            .group_by(
                self.model.id,
                subquery.c.job_id,
                subquery.c.proposals_views,
                favorite_subquery.c.is_favorite,
                proposal_subquery.c.is_applied,
                User.last_visited_at,
            )
            .offset(skip)
            .limit(limit)
        )
        if author_id:
            statement = statement.where(self.model.author_id == author_id)
        if favorite:
            statement = statement.where(
                and_(
                    Favorite.job_id == self.model.id,
                    Favorite.user_id == current_user_id,
                )
            )
        if filters:
            if filters.accepted_languages__in:
                statement = statement.filter(
                    self.model.accepted_languages.overlap(
                        filters.accepted_languages__in
                    )
                )
                filters.accepted_languages__in = None
            statement = filters.filter(statement)
        context = {
            "author": (self.model.author, "last_visited_at"),
        }

        statement = await self._apply_sorting(
            statement, sort_by, sort_order, context
        )
        result = await db.execute(statement)
        rows = result.unique().mappings().all()
        return await response_with_count(limit, skip, rows)

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
        subquery = await self._get_subquery_for_job_view(
            obj_id=self.model.id,
            current_user_id=current_user_id,
            current_user_ip=current_user_ip,
        )
        statement = (
            select(
                self.model,
                func.count(distinct(Proposal.id)).label("proposals_count"),
                (
                    func.count(distinct(Proposal.id)).label("proposals_count")
                    - func.coalesce(subquery.c.proposals_views, 0)
                ).label("new_proposals_count"),
                func.bool_or(subquery.c.existing_view).label("existing_view"),
            )
            .outerjoin(subquery, subquery.c.job_id == self.model.id)
            .outerjoin(self.model.proposals)
            .where(self.model.id.in_(ids))
            .options(
                joinedload(self.model.job_views),
            )
            .group_by(
                self.model.id,
                subquery.c.job_id,
                subquery.c.proposals_views,
                subquery.c.existing_view,
            )
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
        subquery = await self._get_subquery_for_job_view(
            obj_id=self.model.id,
            current_user_id=author_id,
        )
        all_job_views = aliased(JobView)
        statement = (
            select(
                self.model,
                func.count(distinct(Proposal.id)).label("proposals_count"),
                func.count(distinct(all_job_views.id)).label("views"),
                (
                    func.count(distinct(Proposal.id)).label("proposals_count")
                    - func.coalesce(subquery.c.proposals_views, 0)
                ).label("new_proposals_count"),
                func.bool_or(subquery.c.existing_view).label("existing_view"),
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
            .group_by(
                self.model.id, subquery.c.job_id, subquery.c.proposals_views
            )
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
        return await response_with_count(limit, skip, rows)

    async def get_jobs_applied_by_specialist(
        self,
        db: AsyncSession,
        current_user_id: int,
        favorite: bool,
        filters: Optional[JobFilter] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Dict:
        subquery = await self._get_subquery_for_job_view(
            obj_id=self.model.id, current_user_id=current_user_id
        )
        favorite_subquery = await self._get_subquery_for_favorite_job(
            job_id=self.model.id,
            current_user_id=current_user_id,
        )
        proposal_subquery = await self._get_subquery_for_job_proposal(
            job_id=self.model.id, current_user_id=current_user_id
        )
        all_job_views = aliased(JobView)
        proposals_alias = aliased(Proposal)
        statement = (
            select(
                self.model,
                func.count(distinct(proposals_alias.id)).label(
                    "proposals_count"
                ),
                func.count(distinct(all_job_views.id)).label("views"),
                (
                    func.count(distinct(proposals_alias.id)).label(
                        "proposals_count"
                    )
                    - func.coalesce(subquery.c.proposals_views, 0)
                ).label("new_proposals_count"),
                func.bool_or(subquery.c.existing_view).label("existing_view"),
                func.count(self.model.id).over().label("total_count"),
                favorite_subquery.c.is_favorite.label("is_favorite"),
                proposal_subquery.c.is_applied.label("is_applied"),
            )
            .outerjoin(all_job_views, all_job_views.job_id == self.model.id)
            .outerjoin(
                proposals_alias, proposals_alias.job_id == self.model.id
            )
            .outerjoin(subquery, subquery.c.job_id == self.model.id)
            .outerjoin(
                favorite_subquery, favorite_subquery.c.job_id == self.model.id
            )
            .outerjoin(
                proposal_subquery, proposal_subquery.c.job_id == self.model.id
            )
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
                and_(
                    Proposal.user_id == current_user_id,
                    Proposal.job_id == self.model.id,
                ),
            )
            .options(
                selectinload(self.model.author),
                selectinload(self.model.coauthors),
                selectinload(self.model.contact_persons),
                selectinload(self.model.city).selectinload(City.country),
                selectinload(self.model.specializations).joinedload(
                    Specialization.direction
                ),
                selectinload(self.model.proposals).load_only(Proposal.id),
                with_loader_criteria(
                    self.model.proposals,
                    Proposal.user_id == current_user_id,
                ),
            )
            .order_by(desc(self.model.created_at))
            .group_by(
                self.model.id,
                subquery.c.job_id,
                subquery.c.proposals_views,
                favorite_subquery.c.is_favorite,
                proposal_subquery.c.is_applied,
            )
            .offset(skip)
            .limit(limit)
        )
        if favorite:
            statement = statement.where(
                and_(
                    Favorite.job_id == self.model.id,
                    Favorite.user_id == current_user_id,
                )
            )
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
        return await response_with_count(limit, skip, rows)

    @staticmethod
    async def _get_subquery_for_job_view(
        obj_id: Union[int, InstrumentedAttribute],
        current_user_id: Optional[int] = None,
        current_user_ip: Optional[str] = None,
    ) -> Subquery:
        if current_user_id is None:
            case_ = JobView.user_id == current_user_id
        else:
            case_ = JobView.ip_address == current_user_ip
        return (
            select(
                JobView.job_id,
                JobView.proposals_views,
                case(
                    (case_, True),
                    else_=False,
                ).label("existing_view"),
            )
            .where(JobView.job_id == obj_id)
            .subquery()
        )

    @staticmethod
    async def _get_subquery_for_favorite_job(
        job_id: int,
        current_user_id: Optional[int] = None,
    ) -> Select:
        if current_user_id:
            favorite_subquery = (
                select(
                    Favorite.job_id,
                    literal(True).label("is_favorite"),
                )
                .where(
                    Favorite.user_id == current_user_id,
                    Favorite.job_id == job_id,
                )
                .subquery()
            )
        else:
            favorite_subquery = select(
                Favorite.job_id,
                literal(False).label("is_favorite"),
            ).subquery()
        return favorite_subquery

    @staticmethod
    async def _get_subquery_for_job_proposal(
        job_id: int,
        current_user_id: Optional[int] = None,
    ) -> Select:
        if current_user_id:
            is_applied_subquery = (
                select(
                    Proposal.job_id,
                    literal(True).label("is_applied"),
                )
                .where(
                    Proposal.user_id == current_user_id,
                    Proposal.job_id == job_id,
                )
                .subquery()
            )
        else:
            is_applied_subquery = select(
                Proposal.job_id,
                literal(False).label("is_applied"),
            ).subquery()
        return is_applied_subquery

    async def get_jobs_count_for_author(
        self, db: AsyncSession, author_id: int
    ) -> tuple:
        statement = select(
            func.coalesce(
                func.sum(case((self.model.is_archived.is_(True), 1), else_=0)),
                0,
            ).label("archived_jobs_count"),
            func.coalesce(
                func.sum(case((self.model.is_draft.is_(True), 1), else_=0)), 0
            ).label("draft_jobs_count"),
            func.coalesce(
                func.sum(
                    case(
                        (
                            and_(
                                self.model.is_archived.is_(False),
                                self.model.is_draft.is_(False),
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label("published_jobs_count"),
        ).where(self.model.author_id == author_id)
        result = await db.execute(statement)
        return result.fetchone()

    @staticmethod
    async def _apply_sorting(
        statement: Select,
        sort_by: Optional[str],
        sort_order: SortOrder = SortOrder.asc,
        context: Optional[dict] = None,
    ) -> Select:
        model, field_name = context.get(sort_by, (User, "last_visited_at"))
        order_field = getattr(model, field_name)

        if sort_by == "price":
            order_expression = (
                order_field.asc()
                if sort_order == SortOrder.asc
                else order_field.desc()
            )
        else:
            order_expression = order_field.desc()
        return statement.order_by(nullslast(order_expression))


crud_job = CRUDJobWithCounters(Job)
