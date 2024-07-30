from datetime import datetime
from typing import Any, List, Optional

from fastapi import Query
from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter
from sqlalchemy import or_

from api.filters.city import CityFilter
from api.filters.timezone import TimezoneFilter
from api.filters.user_specialist import SpecializationFilter
from models import Event, User
from constants.i18n import EventLanguage
from constants.event import EventType

from api.filters.base_filters import IsDraftAndIsArchivedFilters
from utilities.search import get_transliterated_value


class EventSearchFilter(Filter):
    query_search: Optional[str] = None

    class Constants(Filter.Constants):
        model = Event

    async def filter(self, query: Query) -> Query:
        for field_name, field_value in self:
            if field_name == "query_search" and field_value:
                transliterated_query = await get_transliterated_value(
                    field_value
                )
                search_term = f"%{field_value}%"
                transliterated_search_term = f"%{transliterated_query}%"

                query = query.filter(
                    or_(
                        Event.title.ilike(search_term),
                        Event.description.ilike(search_term),
                        Event.title.ilike(transliterated_search_term),
                        Event.description.ilike(transliterated_search_term),
                    )
                )

            elif hasattr(Event, field_name):
                model_field = getattr(Event, field_name)
                query = query.filter(model_field == field_value)

        return query


class EventFilters(Filter):
    is_free: Optional[bool] = None
    is_online: Optional[bool] = None
    event_type__in: Optional[List[EventType]] = None
    timezone: Optional[TimezoneFilter] = FilterDepends(
        with_prefix("timezone", TimezoneFilter)
    )
    start_datetime__gte: Optional[datetime] = None
    end_datetime__lte: Optional[datetime] = None
    specializations: Optional[SpecializationFilter] = FilterDepends(
        with_prefix("specialization", SpecializationFilter)
    )
    city: Optional[CityFilter] = FilterDepends(with_prefix("city", CityFilter))
    language__in: Optional[List[EventLanguage]] = None
    search: Optional[str] = None

    class Constants(Filter.Constants):
        model = Event

    async def filter(self, query: Query) -> Query:
        async def _apply_filter(q: Query, name: str, value: Any) -> Query:
            if name == "search":
                return await EventSearchFilter(query_search=value).filter(q)
            return filter_map[name](q, value)

        filter_map = {
            "is_free": lambda q, v: q.filter(Event.is_free == v),
            "is_online": lambda q, v: q.filter(Event.is_online == v),
            "event_type__in": lambda q, v: q.filter(Event.event_type.in_(v)),
            "start_datetime__gte": lambda q, v: q.filter(
                Event.start_datetime >= v
            ),
            "end_datetime__lte": lambda q, v: q.filter(
                Event.end_datetime <= v
            ),
            "timezone": lambda q, v: v.filter(q),
            "city": lambda q, v: v.filter(q),
            "language__in": lambda q, v: q.filter(Event.language.in_(v)),
            "specializations": lambda q, v: v.filter(q),
            "search": lambda q, _: q,
        }

        for field_name, field_value in self:
            if field_value is not None and field_name in filter_map:
                query = await _apply_filter(query, field_name, field_value)

        return query


class EventParticipantsFilter(Filter):
    search: Optional[str] = None

    class Constants(Filter.Constants):
        model = User

    async def filter(self, query: Query) -> Query:
        for field_name, field_value in self:
            if field_name == "search" and field_value:
                transliterated_query = await get_transliterated_value(
                    field_value
                )
                search_term = f"%{field_value}%"
                transliterated_search_term = f"%{transliterated_query}%"

                query = query.filter(
                    or_(
                        User.first_name.ilike(search_term),
                        User.second_name.ilike(search_term),
                        User.username.ilike(search_term),
                        User.email.ilike(search_term),
                        User.first_name.ilike(transliterated_search_term),
                        User.second_name.ilike(transliterated_search_term),
                        User.username.ilike(transliterated_search_term),
                        User.email.ilike(transliterated_search_term),
                    )
                )

            elif hasattr(User, field_name):
                model_field = getattr(User, field_name)
                query = query.filter(model_field == field_value)

        return query


class AuthorEventFilters(IsDraftAndIsArchivedFilters):
    class Constants(IsDraftAndIsArchivedFilters.Constants):
        model = Event
