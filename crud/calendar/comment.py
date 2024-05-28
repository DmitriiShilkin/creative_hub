from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from crud.async_crud import BaseAsyncCRUD
from models.calendar import CalendarEventComment
from schemas.calendar.comments import CommentCreate, CommentResponse


class CommentCRUD(
    BaseAsyncCRUD[CalendarEventComment, CommentCreate, CommentResponse]
):
    async def get_by_id(
        self,
        db: AsyncSession,
        obj_id: int,
    ) -> Optional[CalendarEventComment]:
        statement = (
            select(self.model)
            .options(
                joinedload(self.model.author), joinedload(self.model.event)
            )
            .where(self.model.id == obj_id)
        )
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_multi_by_event_id(
        self,
        db: AsyncSession,
        event_id: int,
    ) -> List[CalendarEventComment]:
        statement = (
            select(self.model)
            .options(joinedload(self.model.author))
            .where(self.model.event_id == event_id)
        )
        result = await db.execute(statement)
        return result.scalars().all()


calendar_comments_crud = CommentCRUD(CalendarEventComment)
