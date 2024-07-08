from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import func, insert, not_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload, with_loader_criteria

from api.filters.event import EventFilters
from constants.i18n import Languages
from crud.async_crud import BaseAsyncCRUD
from models import Event
from models.city import City
from models.m2m import EventParticipants
from models.organisation.organisation import Organisation
from models.user.user import User
from models.user.user_specialization import UserSpecialization
from schemas.event import EventCreateDB, EventUpdateDB
from utilities.i18n import detect_language


class CRUDEvent(BaseAsyncCRUD[Event, EventCreateDB, EventUpdateDB]):
    def __init__(self, model):
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

    async def get_multi(
        self,
        db: AsyncSession,
        locale: Languages,
        filters: Optional[EventFilters] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Event]:
        statement = (
            select(
                self.model,
                func.count(EventParticipants.user_id).label(
                    "participants_count"
                ),
            )
            .outerjoin(self.model.city)
            .outerjoin(City.translation_model)
            .outerjoin(self.model.specializations)
            .outerjoin(
                EventParticipants, EventParticipants.event_id == self.model.id
            )
            .where(
                self.model.is_draft.is_(False),
                self.model.end_datetime > datetime.now(tz=timezone.utc),
            )
            .options(
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
            .group_by(self.model.id)
            .offset(skip)
            .limit(limit)
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
        result = result.unique().mappings().all()
        events = []
        for event in result:
            e = event["Event"]
            e.participants_count = event["participants_count"]
            events.append(e)
        return events

    async def get_multi_by_author(
        self,
        db: AsyncSession,
        locale: Languages,
        author_id: Optional[int],
        filters: Optional[EventFilters] = None,
        is_for_creator: Optional[bool] = False,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Event]:
        statement = (
            select(
                self.model,
                func.count(EventParticipants.user_id).label(
                    "participants_count"
                ),
            )
            .outerjoin(self.model.city)
            .outerjoin(City.translation_model)
            .outerjoin(self.model.specializations)
            .outerjoin(
                EventParticipants, EventParticipants.event_id == self.model.id
            )
            .where(
                self.model.creator_id == author_id,
                self.model.end_datetime > datetime.now(tz=timezone.utc),
            )
            .options(
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
            .group_by(self.model.id)
            .offset(skip)
            .limit(limit)
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
        if not is_for_creator:
            statement = statement.where(self.model.is_draft.is_(False))

        result = await db.execute(statement)
        result = result.unique().mappings().all()
        events = []
        for event in result:
            e = event["Event"]
            e.participants_count = event["participants_count"]
            events.append(e)
        return events

    async def get_by_id_extended(
        self, db: AsyncSession, obj_id: int, author_id: Optional[int] = None
    ) -> Optional[Event]:
        statement = (
            select(
                self.model,
                func.count(EventParticipants.user_id).label(
                    "participants_count"
                ),
            )
            .outerjoin(
                EventParticipants, EventParticipants.event_id == self.model.id
            )
            .options(
                *self.common_options,
                *self.user_options,
                *self.contact_persons_options,
                *self.organisations_options,
                *self.participants_options,
            )
            .where(self.model.id == obj_id)
            .group_by(self.model.id)
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
        result = result.unique().mappings().all()
        events = []
        for event in result:
            e = event["Event"]
            e.participants_count = event["participants_count"]
            events.append(e)
        return events[0] if events else None

    async def create(
        self,
        db: AsyncSession,
        *,
        create_schema: EventCreateDB,
        commit: bool = True,
    ) -> Event:
        data = create_schema.model_dump(exclude_unset=True)
        stmt = (
            insert(self.model)
            .values(**data)
            .returning(self.model)
            .options(
                selectinload(self.model.specializations),
                selectinload(self.model.organizers),
                selectinload(self.model.speakers),
                selectinload(self.model.organisations),
                selectinload(self.model.contact_persons),
                selectinload(self.model.creator),
            )
        )
        res = await db.execute(stmt)
        if commit:
            await db.commit()
        return res.scalars().first()


crud_event = CRUDEvent(Event)
