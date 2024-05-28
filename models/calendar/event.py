from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from constants.calendar.event import (
    CalendarEventPriority,
    CalendarEventRepeatability,
    CalendarEventType,
)

# from constants.calendar.timezone import TimeZone
from models.base import Base
from models.m2m import CalendarEventUsers

if TYPE_CHECKING:
    from models.calendar import CalendarEventComment
    from models.user import User


class CalendarEvent(Base):
    """
    Модель события

    ## Attrs
        - id :int - идентификатор события
        - title : str - название события
        - event_type: str (Enum) - тип события
        - priority : str (Enum) - приоритет события
        - repeatability :  str (Enum) - повторяемость события
        - start_time : datetime - дата и время начала
        - end_time : datetime - дата и время окончания
        - created_at: datetime - дата и время создания события
        - description : str - описание событие
        - organizer_id : int - FK User (id пользователя
          организатора  события)
        - organizer : User - пользователь организатор события
        - participants: [List["User"]] -  Участники события (м2м)
        - comments:[List["CalendarEventComment"]] - Комментарии
            к событию
    """

    __tablename__ = "calendar_event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str]
    event_type: Mapped[CalendarEventType] = mapped_column(
        ENUM(CalendarEventType, create_type=False),
    )
    priority: Mapped[CalendarEventPriority] = mapped_column(
        ENUM(CalendarEventPriority, create_type=False),
    )
    repeatability: Mapped[CalendarEventRepeatability] = mapped_column(
        ENUM(CalendarEventRepeatability, create_type=False),
    )
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    # timezone: Mapped[TimeZone] = mapped_column(
    #     ENUM(TimeZone, create_type=False)
    # )
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    organizer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE")
    )
    organizer: Mapped["User"] = relationship(
        "User", back_populates="calendar_events_organizer"
    )
    participants: Mapped[List["User"]] = relationship(
        "User",
        back_populates="calendar_events_participant",
        secondary=CalendarEventUsers.__table__,
    )
    calendar_comments: Mapped[List["CalendarEventComment"]] = relationship(
        "CalendarEventComment",
        back_populates="event",
        cascade="all, delete",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"{self.id}"
