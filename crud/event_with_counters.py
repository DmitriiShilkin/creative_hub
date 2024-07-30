from datetime import datetime, UTC
from typing import Dict, List, Optional, Type

from sqlalchemy import (
    RowMapping,
    and_,
    distinct,
    exists,
    func,
    or_,
    select,
    literal,
    case,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    aliased,
    contains_eager,
    joinedload,
    with_loader_criteria,
)
from sqlalchemy.sql.selectable import Select

from api.filters.event import (
    AuthorEventFilters,
    EventFilters,
    EventParticipantsFilter,
)
from constants.i18n import Languages
from crud.crud_mixins import BaseCRUD, ReadAsync
from crud.options import specialisations, city_and_country
from models import (
    City,
    Event,
    EventView,
    Favorite,
    Organisation,
    User,
    UserSpecialization,
    Specialization,
)
from models.event_participants import EventParticipants
from models.m2m import EventSpecializations
from models.country import Country
from models.timezone import Timezone
from utilities.exception import QuerySet
from utilities.i18n import detect_language
from utilities.paginated_response import response_with_count


class CRUDEventWithCounters(BaseCRUD[Event], ReadAsync[Event]):
    def __init__(self, model: Type[Event]) -> None:
        super().__init__(model)
        self.common_options = (
            joinedload(self.model.specializations).options(*specialisations),
            joinedload(self.model.city).options(*city_and_country),
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
            joinedload(self.model.organisations).options(
                joinedload(Organisation.private_sites),
                joinedload(Organisation.translations),
            ),
        )

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
        favorite_subquery = await self._get_subquery_for_favorite_event(
            event_id=obj_id, current_user_id=author_id
        )
        attended_subquery = await self._get_subquery_for_attended_event(
            event_id=obj_id, current_user_id=author_id
        )
        all_event_views = aliased(EventView)
        statement = (
            select(
                self.model,
                func.count(distinct(EventParticipants.user_id)).label(
                    "participants_count"
                ),
                func.count(distinct(all_event_views.id)).label("views"),
                (
                    func.count(distinct(EventParticipants.user_id)).label(
                        "participants_count"
                    )
                    - func.coalesce(subquery.c.participants_views, 0)
                ).label("new_participants_count"),
                favorite_subquery.c.is_favorite.label("is_favorite"),
                attended_subquery.c.is_attended.label("is_attended"),
            )
            .outerjoin(
                EventParticipants, EventParticipants.event_id == self.model.id
            )
            .outerjoin(
                all_event_views, all_event_views.event_id == self.model.id
            )
            .outerjoin(subquery, subquery.c.event_id == self.model.id)
            .outerjoin(
                favorite_subquery,
                favorite_subquery.c.event_id == self.model.id,
            )
            .outerjoin(
                attended_subquery,
                attended_subquery.c.event_id == self.model.id,
            )
            .where(
                self.model.id == obj_id,
            )
            .options(
                contains_eager(self.model.event_views, alias=subquery),
                *self.common_options,
                *self.user_options,
                *self.contact_persons_options,
                *self.organisations_options,
            )
            .group_by(
                self.model.id,
                subquery.c.participants_views,
                subquery.c.id,
                subquery.c.event_id,
                subquery.c.ip_address,
                subquery.c.user_id,
                favorite_subquery.c.is_favorite,
                attended_subquery.c.is_attended,
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
        favorite_subquery = await self._get_subquery_for_favorite_event(
            event_id=self.model.id, current_user_id=current_user_id
        )
        attended_subquery = await self._get_subquery_for_attended_event(
            event_id=self.model.id, current_user_id=current_user_id
        )
        all_event_views = aliased(EventView)
        statement = (
            select(
                self.model,
                func.count(distinct(EventParticipants.user_id)).label(
                    "participants_count"
                ),
                func.count(distinct(all_event_views.id)).label("views"),
                (
                    func.count(distinct(EventParticipants.user_id)).label(
                        "participants_count"
                    )
                    - func.coalesce(subquery.c.participants_views, 0)
                ).label("new_participants_count"),
                func.count().over().label("total_count"),
                exists(subquery.c.event_id).label("is_viewed_by_current_user"),
                favorite_subquery.c.is_favorite.label("is_favorite"),
                attended_subquery.c.is_attended.label("is_attended"),
            )
            .outerjoin(
                EventParticipants, EventParticipants.event_id == self.model.id
            )
            .outerjoin(
                all_event_views, all_event_views.event_id == self.model.id
            )
            .outerjoin(Timezone, Timezone.id == Event.timezone_id)
            .outerjoin(subquery, subquery.c.event_id == self.model.id)
            .outerjoin(
                favorite_subquery,
                favorite_subquery.c.event_id == self.model.id,
            )
            .outerjoin(
                attended_subquery,
                attended_subquery.c.event_id == self.model.id,
            )
            .outerjoin(City, City.id == self.model.city_id)
            .outerjoin(City.translation_model)
            .outerjoin(Country, City.country_id == Country.id)
            .outerjoin(
                EventSpecializations,
                EventSpecializations.event_id == self.model.id,
            )
            .outerjoin(
                Specialization,
                Specialization.id == EventSpecializations.specialization_id,
            )
            .where(
                self.model.end_datetime > datetime.now(tz=UTC),
                self.model.is_archived.is_(False),
            )
            .options(
                contains_eager(self.model.event_views, alias=subquery),
                *self.common_options,
                *self.user_options,
                *self.contact_persons_options,
                *self.organisations_options,
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
                favorite_subquery.c.is_favorite,
                attended_subquery.c.is_attended,
            )
            .offset(skip)
            .limit(limit)
        )

        if author_id:
            statement = statement.where(
                self.model.creator_id == author_id
            ).where(self.model.is_draft.is_(False))
        else:
            statement = statement.where(self.model.is_draft.is_(False))
        if favorite:
            statement = statement.where(
                and_(
                    Favorite.event_id == self.model.id,
                    Favorite.user_id == current_user_id,
                )
            )
        if filters:
            statement = await filters.filter(statement)
            if filters.specializations and filters.specializations.id__in:
                statement = statement.where(
                    Specialization.id.in_(filters.specializations.id__in)
                )
            if filters.city:
                if filters.city.name__ilike:
                    request_language = detect_language(
                        filters.city.name__ilike
                    )
                    if request_language:
                        locale = request_language
                statement = filters.city.filter(statement)
        result = await db.execute(statement)
        rows = result.unique().mappings().all()
        return await response_with_count(limit, skip, rows)

    async def get_multi_for_author(
        self,
        db: AsyncSession,
        locale: Languages,
        filters: Optional[AuthorEventFilters] = None,
        skip: int = 0,
        limit: int = 20,
        author_id: Optional[int] = None,
    ) -> Optional[Dict]:
        subquery = await self._get_subquery_for_event_view(
            current_user_id=author_id
        )
        all_event_views = aliased(EventView)
        statement = (
            select(
                self.model,
                func.count(distinct(EventParticipants.user_id)).label(
                    "participants_count"
                ),
                func.count(distinct(all_event_views.id)).label("views"),
                (
                    func.count(distinct(EventParticipants.user_id)).label(
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
            .offset(skip)
            .limit(limit)
        )
        if filters:
            statement = await filters.filter_query(statement)

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
                func.count(distinct(EventParticipants.user_id)).label(
                    "participants_count"
                ),
                (
                    func.count(distinct(EventParticipants.user_id)).label(
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

    async def get_multi_participants_by_event_id(
        self,
        db: AsyncSession,
        event_id: int,
        filters: Optional[EventParticipantsFilter] = None,
        limit: int = 0,
        skip: int = 20,
    ) -> Optional[Dict]:
        statement = (
            select(
                User.first_name,
                User.second_name,
                User.username,
                User.email,
                User.uid,
                User.photo,
                func.count().over().label("total_count"),
            )
            .join(EventParticipants, EventParticipants.user_id == User.id)
            .where(EventParticipants.event_id == event_id)
            .offset(skip)
            .limit(limit)
        )
        if filters:
            statement = await filters.filter(statement)
        result = await db.execute(statement)
        rows = result.unique().mappings().all()
        return await response_with_count(limit, skip, rows)

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

    async def _get_subquery_for_favorite_event(
        self,
        event_id: int,
        current_user_id: Optional[int] = None,
    ) -> Select:
        if current_user_id:
            favorite_subquery = (
                select(
                    Favorite.event_id,
                    literal(True).label("is_favorite"),
                )
                .where(
                    Favorite.user_id == current_user_id,
                    Favorite.event_id == event_id,
                )
                .subquery()
            )
        else:
            favorite_subquery = select(
                Favorite.event_id,
                literal(False).label("is_favorite"),
            ).subquery()
        return favorite_subquery

    async def get_events_count_for_author(
        self, db: AsyncSession, author_id: int
    ) -> tuple:
        statement = select(
            func.coalesce(
                func.sum(case((self.model.is_archived.is_(True), 1), else_=0)),
                0,
            ).label("archived_events_count"),
            func.coalesce(
                func.sum(case((self.model.is_draft.is_(True), 1), else_=0)), 0
            ).label("draft_events_count"),
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
            ).label("published_events_count"),
        ).where(self.model.creator_id == author_id)
        result = await db.execute(statement)
        return result.fetchone()

    async def _get_subquery_for_attended_event(
        self,
        event_id: int,
        current_user_id: Optional[int] = None,
    ) -> Select:
        if current_user_id:
            attended_subquery = (
                select(
                    EventParticipants.event_id,
                    literal(True).label("is_attended"),
                )
                .where(
                    EventParticipants.user_id == current_user_id,
                    EventParticipants.event_id == event_id,
                )
                .subquery()
            )
        else:
            attended_subquery = select(
                EventParticipants.event_id,
                literal(False).label("is_attended"),
            ).subquery()
        return attended_subquery


crud_ewc = CRUDEventWithCounters(Event)
