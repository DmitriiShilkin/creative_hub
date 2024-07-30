from datetime import datetime
from typing import TYPE_CHECKING, Optional

from fastapi_storages.integrations.sqlalchemy import FileType
from sqlalchemy import (
    ARRAY,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression

from constants.event import EventType, RegistrationEndType
from constants.i18n import EventLanguage
from models.base import Base
from models.m2m import (
    EventContactPerson,
    EventOrganizers,
    EventsOrganisations,
    EventSpeakers,
    EventSpecializations,
)
from storages.s3_events import events_storage

if TYPE_CHECKING:
    from models.contact_person import ContactPerson
    from models.event_participants import EventParticipants
    from models import (
        City,
        EventView,
        Favorite,
        Organisation,
        Specialization,
        Timezone,
    )

    from .user import User


class Event(Base):
    """
    Модель события.

    # Attrs:
        - id: int
        - creator_id: int - Идентификатор пользователя, создавшего событие.
        - creator: User - Объект пользователя, являющегося создателем события.
        - photo: FileType - Поле для хранения фотографии события.
        - event_cover: FileType - Поле для хранения обложки события.
        - title: str - Название события, до 120 символов.
        - description: str - Подробное описание события.
        - event_type: EventType - Тип события, определенный перечислением.
        - language: EventLanguage - Язык, на котором проводится событие.
        - extra_language: EventLanguage - доп. языки.
        - timezone_id (int): Идентификатор часового пояса.
        - is_free: bool - Флаг, указывающий, бесплатно ли событие.
        - specializations: Specialization -  Список специализаций
        - is_online: bool - Флаг, указывающий, проводится ли событие онлайн.
        - city_id: int - Идентификатор города, где проводится событие.
        - places: JSON - Адрес и Название места проведения события.
        - online_link: str - Ссылка для онлайн-доступа к событию.
        - start_datetime: DateTime - Дата и время начала события.
        - end_datetime: DateTime - Дата и время окончания события.
        - registration_end_datetime: DateTime - дата и время окончания регистр
        - registration_end_type: RegistrationEndType - тип окончания регист.
        - registration_end_interval: int - интервал напоминания.
        - registration_end_unit: ReminderUnits - Ед. измерения интервала.
        - reminder_before_event: int - Интервал напоминания перед событием.
        - reminder_units: ReminderUnits - Ед. измерения интервала.
        - reminder_time: Time - Время напоминаня
        - country: Country - Объект страны, связанный с событием.
        - city: City - Объект города, связанный с событием.
        - organizers: User - Список пользователей, являющихся организаторами.
        - speakers: User - Список пользователей, являющихся спикерами события.
        - contact_persons: ContactPerson - Список контактных лиц события.
        - organisations: Organisation - Компании партнёры.
        - participants: User - список пользователей, ивента
        - published_at: DateTime - Дата и время опубликования события.
    """

    __tablename__ = "event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo: Mapped[Optional[FileType]] = mapped_column(
        FileType(storage=events_storage)
    )
    event_cover: Mapped[Optional[FileType]] = mapped_column(
        FileType(storage=events_storage)
    )
    event_type: Mapped[Optional[EventType]] = mapped_column(
        ENUM(EventType, create_type=False), nullable=True
    )
    language: Mapped[Optional[EventLanguage]] = mapped_column(
        ENUM(EventLanguage, create_type=False)
    )
    extra_languages: Mapped[list[EventLanguage]] = mapped_column(
        ARRAY(ENUM(EventLanguage, create_type=False))
    )
    is_free: Mapped[bool] = mapped_column(Boolean, default=True)
    is_online: Mapped[bool] = mapped_column(Boolean, default=True)
    is_draft: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.true()
    )
    is_archived: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.false()
    )
    timezone_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("timezone.id"), nullable=True
    )
    creator_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False
    )
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="created_events",
    )
    city_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("city.id"), nullable=True
    )
    city: Mapped["City"] = relationship("City", back_populates="events")
    places: Mapped[list] = mapped_column(JSONB, default=JSONB.NULL)
    online_links: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(String), default=[], nullable=True
    )
    start_datetime: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    end_datetime: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    registration_end_datetime: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    registration_end_type: Mapped[Optional[RegistrationEndType]] = (
        mapped_column(
            ENUM(
                RegistrationEndType, default=RegistrationEndType.AT_EVENT_START
            ),
        )
    )
    reminders: Mapped[Optional[list]] = mapped_column(
        JSONB, default=JSONB.NULL
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    organizers: Mapped[list["User"]] = relationship(
        "User",
        secondary=EventOrganizers.__table__,
        back_populates="organized_events",
    )
    speakers: Mapped[list["User"]] = relationship(
        "User",
        secondary=EventSpeakers.__table__,
        back_populates="speaking_events",
    )
    contact_persons: Mapped[list["ContactPerson"]] = relationship(
        "ContactPerson",
        back_populates="events",
        secondary=EventContactPerson.__table__,
    )
    specializations: Mapped[list["Specialization"]] = relationship(
        "Specialization",
        secondary=EventSpecializations.__table__,
        back_populates="events",
    )
    organisations: Mapped[list["Organisation"]] = relationship(
        "Organisation",
        back_populates="events",
        secondary=EventsOrganisations.__table__,
    )
    timezone: Mapped["Timezone"] = relationship(
        "Timezone", back_populates="events"
    )
    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite", back_populates="event"
    )
    participants: Mapped[list["EventParticipants"]] = relationship(
        "EventParticipants",
        back_populates="event",
        cascade="all, delete, delete-orphan",
        passive_deletes=True,
    )
    event_views: Mapped[list["EventView"]] = relationship(
        "EventView",
        back_populates="event",
        cascade="all, delete",
        passive_deletes=True,
    )

    def __str__(self) -> str:
        return self.title
