from datetime import datetime, UTC
from typing import Dict, List, Optional

from sqlalchemy import (
    RowMapping,
    and_,
    distinct,
    exists,
    func,
    not_,
    or_,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    aliased,
    contains_eager,
    joinedload,
    with_loader_criteria,
)
from sqlalchemy.sql.selectable import Select

from api.filters.event import AuthorEventFilters, EventFilters
from constants.i18n import Languages
from crud.crud_mixins import BaseCRUD, ReadAsync
from models import (
    City,
    Event,
    EventView,
    Favorite,
    Organisation,
    User,
    UserSpecialization,
)
from models.m2m import EventParticipants
from utilities.exception import QuerySet
from utilities.i18n import detect_language
from utilities.paginated_response import response_with_count


class CRUDEventWithCounters(BaseCRUD[Event], ReadAsync[Event]):
    def __init__(self, model: Event) -> None:
        super().__init__(model)
        self.common_options = (
            joinedload(self.model.specializations),
            joinedload(self.model.city).joinedload(City.country),
            joinedload(self.model.timezone),
        )
        self.user_options = (
            joinedload(self.model.organizers)
            .joinedload(User.specialization)
            .joinedload(UserSpecialization.specializations),
            joinedload(self.model.speakers)
            .joinedload(User.specialization)
            .joinedload(UserSpecialization.specializations),
            joinedload(self.model.creator),
        )
        self.contact_persons_options = (
            joinedload(self.model.contact_persons),
        )
        self.organisations_options = (
            joinedload(self.model.organisations).joinedload(
                Organisation.private_sites
            ),
        )
        self.participants_options = (joinedload(self.model.participants),)

    async def get_by_id(
        self,
        db: AsyncSession,
        *,
        obj_id: int,
        author_id: Optional[int] = None,
        current_user_ip: Optional[str] = None,
    ) -> Optional[Dict]:
        subquery = await self._get_subquery_for_event_view(
            author_id, current_user_ip
        )
        all_event_views = aliased(EventView)
        statement = (
            select(
                self.model,
                func.count(EventParticipants.user_id).label(
                    "participants_count"
                ),
                func.count(distinct(all_event_views.id)).label("views"),
                (
                    func.count(EventParticipants.user_id).label(
                        "participants_count"
                    )
                    - func.coalesce(subquery.c.participants_views, 0)
                ).label("new_participants_count"),
            )
            .outerjoin(
                EventParticipants, EventParticipants.event_id == self.model.id
            )
            .outerjoin(
                all_event_views, all_event_views.event_id == self.model.id
            )
            .outerjoin(subquery, subquery.c.event_id == self.model.id)
            .where(
                self.model.id == obj_id,
            )
            .options(
                contains_eager(self.model.event_views, alias=subquery),
                *self.common_options,
                *self.user_options,
                *self.contact_persons_options,
                *self.organisations_options,
                *self.participants_options,
            )
            .group_by(
                self.model.id,
                subquery.c.participants_views,
                subquery.c.id,
                subquery.c.event_id,
                subquery.c.ip_address,
                subquery.c.user_id,
            )
        )
        if author_id:
            statement = statement.where(
                or_(
                    self.model.creator_id == author_id,
                    self.model.is_draft.is_(False),
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
        locale: Languages,
        skip: int = 0,
        limit: int = 20,
        author_id: Optional[int] = None,
        current_user_id: Optional[int] = None,
        current_user_ip: Optional[str] = None,
        filters: Optional[EventFilters] = None,
    ) -> Optional[Dict]:
        subquery = await self._get_subquery_for_event_view(
            current_user_id, current_user_ip
        )
        all_event_views = aliased(EventView)
        statement = (
            select(
                self.model,
                func.count(EventParticipants.user_id).label(
                    "participants_count"
                ),
                func.count(distinct(all_event_views.id)).label("views"),
                (
                    func.count(EventParticipants.user_id).label(
                        "participants_count"
                    )
                    - func.coalesce(subquery.c.participants_views, 0)
                ).label("new_participants_count"),
                func.count(self.model.id).over().label("total_count"),
                exists(subquery.c.event_id).label("is_viewed_by_current_user"),
            )
            .outerjoin(
                EventParticipants, EventParticipants.event_id == self.model.id
            )
            .outerjoin(
                all_event_views, all_event_views.event_id == self.model.id
            )
            .outerjoin(subquery, subquery.c.event_id == self.model.id)
            .where(
                self.model.is_draft.is_(False),
                self.model.end_datetime > datetime.now(tz=UTC),
            )
            .options(
                contains_eager(self.model.event_views, alias=subquery),
                *self.common_options,
                *self.user_options,
                *self.contact_persons_options,
                *self.organisations_options,
                *self.participants_options,
                with_loader_criteria(
                    City.translation_model,
                    City.translation_model.locale == locale,
                ),
            )
            .group_by(
                self.model.id,
                subquery.c.participants_views,
                subquery.c.id,
                subquery.c.event_id,
                subquery.c.ip_address,
                subquery.c.user_id,
            )
        )
        if author_id:
            statement = statement.where(
                self.model.creator_id == author_id,
            )
        if favorite:
            statement = statement.where(
                and_(
                    Favorite.event_id == self.model.id,
                    Favorite.user_id == current_user_id,
                )
            )
        if filters:
            if filters.city and filters.city.name__ilike:
                request_language = detect_language(filters.city.name__ilike)
                if request_language:
                    locale = request_language
                statement = filters.filter(statement)
            if filters.city and filters.city.name__not_ilike:
                statement = statement.where(
                    not_(
                        City.translation_model.name.ilike(
                            f"%{filters.city.name__not_ilike}%"
                        )
                    )
                )
        result = await db.execute(statement)
        rows = result.unique().mappings().all()
        return await response_with_count(limit, skip, rows)

    async def get_multi_for_author(
        self,
        db: AsyncSession,
        locale: Languages,
        skip: int = 0,
        limit: int = 20,
        author_id: Optional[int] = None,
        filters: Optional[AuthorEventFilters] = None,
    ) -> Optional[Dict]:
        subquery = await self._get_subquery_for_event_view(
            current_user_id=author_id
        )
        all_event_views = aliased(EventView)
        statement = (
            select(
                self.model,
                func.count(EventParticipants.user_id).label(
                    "participants_count"
                ),
                func.count(distinct(all_event_views.id)).label("views"),
                (
                    func.count(EventParticipants.user_id).label(
                        "participants_count"
                    )
                    - func.coalesce(subquery.c.participants_views, 0)
                ).label("new_participants_count"),
                func.count(self.model.id).over().label("total_count"),
            )
            .outerjoin(
                EventParticipants, EventParticipants.event_id == self.model.id
            )
            .outerjoin(
                all_event_views, all_event_views.event_id == self.model.id
            )
            .outerjoin(subquery, subquery.c.event_id == self.model.id)
            .where(
                self.model.creator_id == author_id,
            )
            .options(
                contains_eager(self.model.event_views, alias=subquery),
                *self.common_options,
                *self.user_options,
                *self.contact_persons_options,
                *self.organisations_options,
                *self.participants_options,
                with_loader_criteria(
                    City.translation_model,
                    City.translation_model.locale == locale,
                ),
            )
            .group_by(
                self.model.id,
                subquery.c.participants_views,
                subquery.c.id,
                subquery.c.event_id,
                subquery.c.ip_address,
                subquery.c.user_id,
            )
        )
        if filters:
            if filters.city and filters.city.name__ilike:
                request_language = detect_language(filters.city.name__ilike)
                if request_language:
                    locale = request_language
                statement = filters.filter(statement)
            if filters.city and filters.city.name__not_ilike:
                statement = statement.where(
                    not_(
                        City.translation_model.name.ilike(
                            f"%{filters.city.name__not_ilike}%"
                        )
                    )
                )
            if filters.is_archived is not None:
                statement = statement.where(
                    self.model.is_archived == filters.is_archived
                )
            if filters.is_draft is not None:
                statement = statement.where(
                    self.model.is_draft == filters.is_draft
                )

        result = await db.execute(statement)
        rows = result.unique().mappings().all()
        return await response_with_count(limit, skip, rows)

    async def get_multi_by_ids(
        self,
        db: AsyncSession,
        ids: List[int],
        current_user_id: Optional[int] = None,
        current_user_ip: Optional[str] = None,
    ) -> Optional[QuerySet[RowMapping]]:
        if not ids:
            return []
        subquery = await self._get_subquery_for_event_view(
            current_user_id, current_user_ip
        )
        statement = (
            select(
                self.model,
                func.count(EventParticipants.user_id).label(
                    "participants_count"
                ),
                (
                    func.count(EventParticipants.user_id).label(
                        "participants_count"
                    )
                    - func.coalesce(subquery.c.participants_views, 0)
                ).label("new_participants_count"),
            )
            .outerjoin(
                EventParticipants, EventParticipants.event_id == self.model.id
            )
            .outerjoin(subquery, subquery.c.event_id == self.model.id)
            .where(
                self.model.id.in_(ids),
                self.model.is_draft.is_(False),
                self.model.end_datetime > datetime.now(tz=UTC),
            )
            .options(
                contains_eager(self.model.event_views, alias=subquery),
            )
            .group_by(
                self.model.id,
                subquery.c.participants_views,
                subquery.c.id,
                subquery.c.event_id,
                subquery.c.ip_address,
                subquery.c.user_id,
            )
        )
        result = await db.execute(statement)
        objects = result.unique().mappings().all()
        result = QuerySet(objects)
        result.model = self.model
        return result

    async def _get_subquery_for_event_view(
        self,
        current_user_id: Optional[int] = None,
        current_user_ip: Optional[str] = None,
    ) -> Select:
        return (
            select(EventView).where(
                or_(
                    EventView.user_id == current_user_id,
                    and_(
                        EventView.user_id.is_(None),
                        EventView.ip_address == current_user_ip,
                    ),
                )
            )
        ).alias("filtered_event_view")


crud_ewc = CRUDEventWithCounters(Event)
