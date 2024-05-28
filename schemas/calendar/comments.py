from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from constants.calendar.comment import MAX_LENGTH_TEXT, MIN_LENGTH_TEXT
from schemas.user.user import UserCalendarResponse


class CommentBase(BaseModel):
    text: str = Field(min_length=MIN_LENGTH_TEXT, max_length=MAX_LENGTH_TEXT)

    class Config:
        from_attributes = True


class CommentCreate(CommentBase):
    ...


class CommentCreateDB(CommentBase):
    author_id: int
    event_id: int


class CommentUpdate(BaseModel):
    text: Optional[str] = Field(
        min_length=MIN_LENGTH_TEXT, max_length=MAX_LENGTH_TEXT, default=None
    )


class CommentResponseBase(CommentBase):
    created_at: datetime


class CommentResponse(CommentResponseBase):
    author: UserCalendarResponse
