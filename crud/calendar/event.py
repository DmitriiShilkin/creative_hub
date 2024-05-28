from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import and_, extract, func, insert, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload

from crud.async_crud import BaseAsyncCRUD
from models.calendar.comment import CalendarEventComment
from models.calendar.event import CalendarEvent
from schemas.calendar.event import (
    CalendarEventCreate,
    CalendarEventCreateDB,
    CalendarEventUpdate,
)


class EventCRUD(
    BaseAsyncCRUD[CalendarEvent, CalendarEventCreate, CalendarEventCreateDB]
):
    async def get_by_id_and_user_id(
        self,
        db: AsyncSession,
        obj_id: int,
        user_id: int,
    ) -> Optional[CalendarEvent]:
        statement = (
            select(self.model)
            .options(
                joinedload(self.model.calendar_comments).joinedload(
                    CalendarEventComment.author
                ),
                joinedload(self.model.participants),
            )
            .where(
                self.model.id == obj_id,
                or_(
                    self.model.organizer_id == user_id,
                    self.model.participants.any(id=user_id),
                ),
            )
        )
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_today_events_by_user_id(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> List[CalendarEvent]:
        today = datetime.now().date()
        statement = select(self.model).where(
            func.date(self.model.start_time) == today,
            or_(
                self.model.organizer_id == user_id,
                self.model.participants.any(id=user_id),
            ),
        )
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_week_events_by_user_id(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> List[CalendarEvent]:
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=7)
        statement = select(self.model).where(
            and_(
                self.model.start_time >= start_of_week,
                self.model.start_time <= end_of_week,
            ),
            or_(
                self.model.organizer_id == user_id,
                self.model.participants.any(id=user_id),
            ),
        )
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_month_events_by_user_id(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> List[CalendarEvent]:
        current_month = datetime.now().month
        statement = select(self.model).where(
            and_(
                extract("month", self.model.start_time) == current_month,
            ),
            or_(
                self.model.organizer_id == user_id,
                self.model.participants.any(id=user_id),
            ),
        )
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_all_events_by_user_id(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> List[CalendarEvent]:
        statement = (
            select(self.model)
            .where(
                or_(
                    self.model.organizer_id == user_id,
                    self.model.participants.any(id=user_id),
                )
            )
            .order_by(self.model.created_at.desc())
        )
        result = await db.execute(statement)
        return result.scalars().all()

    async def create(
        self,
        db: AsyncSession,
        create_schema: CalendarEventCreateDB,
        commit: bool = True,
    ) -> CalendarEvent:
        data = create_schema.model_dump(exclude_unset=True)
        statement = (
            insert(self.model)
            .values(**data)
            .returning(self.model)
            .options(
                selectinload(self.model.participants),
            )
        )
        result = await db.execute(statement)
        if commit:
            await db.commit()
        return result.scalars().first()

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: CalendarEvent,
        update_data: CalendarEventUpdate,
        commit: bool = True,
    ) -> CalendarEvent:
        if isinstance(update_data, BaseModel):
            update_data = update_data.model_dump(exclude_unset=True)
        if not update_data:
            return db_obj
        statement = (
            update(self.model)
            .values(**update_data)
            .where(self.model.id == db_obj.id)
            .returning(self.model)
            .options(
                selectinload(self.model.participants),
            )
        )
        result = await db.execute(statement)
        if commit:
            await db.commit()
        return result.scalars().first()


calendar_event_crud = EventCRUD(CalendarEvent)
