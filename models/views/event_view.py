from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models import Event, User


class EventView(Base):
    """
    Модель просмотра.

    # Attrs:
        - id: int - Уникальный идентификатор просмотра.
        - ip_address: Optional[str] - IP-адрес, с которого был сделан просмотр.
        - participants_views: Optional[int] - Количество просмотренных
         участников
        - user_id: Optional[int] (FK) - Идентификатор пользователя.
        - user: Optional[User] - Пользователь, совершивший просмотр.
        - event_id: Optional[int] (FK) - Идентификатор мероприятия.
        - event: Event - Связанное мероприятие.

    """

    __tablename__ = "event_view"
    __table_args__ = (
        UniqueConstraint("user_id", "event_id"),
        UniqueConstraint("ip_address", "event_id"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ip_address: Mapped[Optional[str]]
    participants_views: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE")
    )
    user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="event_views"
    )
    event_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("event.id", ondelete="CASCADE")
    )
    event: Mapped["Event"] = relationship(
        "Event", back_populates="event_views"
    )
