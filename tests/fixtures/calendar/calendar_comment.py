import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from crud.calendar.comment import calendar_comments_crud
from models.calendar import CalendarEvent, CalendarEventComment
from models.user import User
from schemas.calendar.comments import CommentCreateDB


@pytest_asyncio.fixture
async def calendar_comment_fixture(
    async_session: AsyncSession,
    user_fixture: User,
    calendar_event_fixture: CalendarEvent,
) -> CalendarEventComment:
    schema = CommentCreateDB(
        text="Calendar comment text",
        author_id=user_fixture.id,
        event_id=calendar_event_fixture.id,
    )
    new_calendar_comment = await calendar_comments_crud.create(
        db=async_session,
        create_schema=schema,
    )
    return new_calendar_comment
