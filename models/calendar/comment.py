from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.calendar import CalendarEvent
    from models.user import User


class CalendarEventComment(Base):
    """
    Модель
    комментария к событию

    ## Attrs
        - id: int - идентификатор комментария
        - text: str - текст комментария
        - created_at: datetime - дата и время комментария
        - author_id: int - FK User - идентификатор автора комментария
        - event_id: int - прокомментированное событие FK Event
        - author : User - связь пользователь автор комментария
        - event : Event - связь прокомментированное событие
    """

    __tablename__ = "calendar_event_comment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE")
    )
    author: Mapped["User"] = relationship(
        "User", back_populates="calendar_comments"
    )
    event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("calendar_event.id", ondelete="CASCADE")
    )
    event: Mapped["CalendarEvent"] = relationship(
        "CalendarEvent",
        back_populates="calendar_comments",
    )

    def __repr__(self) -> str:
        return f"{self.id} {self.author_id}"
