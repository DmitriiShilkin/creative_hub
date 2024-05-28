from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from constants.calendar.event import (
    MAX_LENGTH_DESCRIPTION,
    MAX_LENGTH_TITLE,
    MIN_LENGTH_TITLE,
    CalendarEventPriority,
    CalendarEventRepeatability,
    CalendarEventType,
)

# from constants.calendar.timezone import TimeZone
from schemas.calendar.comments import CommentResponse
from schemas.user.user import UserCalendarResponse


class CalendarEventBase(BaseModel):
    title: str = Field(
        min_length=MIN_LENGTH_TITLE,
        max_length=MAX_LENGTH_TITLE,
    )
    event_type: CalendarEventType = Field(
        default=CalendarEventType.NO_CATEGORY
    )
    priority: CalendarEventPriority = Field(
        default=CalendarEventPriority.WITHOUT_PRIORITY
    )
    repeatability: CalendarEventRepeatability = Field(
        default=CalendarEventRepeatability.NO_REPEATS
    )
    start_time: datetime
    end_time: datetime
    # timezone: TimeZone
    description: str = Field(max_length=MAX_LENGTH_DESCRIPTION)

    class Config:
        from_attributes = True


class CalendarEventCreate(CalendarEventBase):
    participants: List[str] = []

    class Config:
        from_attributes = True


class CalendarEventCreateDB(CalendarEventBase):
    organizer_id: int


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = Field(
        min_length=MIN_LENGTH_TITLE, max_length=MAX_LENGTH_TITLE, default=None
    )
    event_type: Optional[CalendarEventType] = Field(
        default=CalendarEventType.NO_CATEGORY
    )
    priority: Optional[CalendarEventPriority] = Field(
        default=CalendarEventPriority.WITHOUT_PRIORITY
    )
    repeatability: Optional[CalendarEventRepeatability] = Field(
        default=CalendarEventRepeatability.NO_REPEATS
    )
    description: Optional[str] = Field(
        max_length=MAX_LENGTH_DESCRIPTION, default=None
    )
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    participants: Optional[List[str]] = []


class CalendarEventResponse(CalendarEventBase):
    ...


class CalendarEventFullResponse(CalendarEventResponse):
    participants: List[UserCalendarResponse]
    calendar_comments: List[CommentResponse]
