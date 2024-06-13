from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from utilities.i18n import CustomTranslatableMixin

if TYPE_CHECKING:
    from models import Event, Organisation, User


class Timezone(Base, CustomTranslatableMixin):
    """
    Модель временных зон.

    # Attrs:
        - id (int): Уникальный идентификатор временной зоны.
        - translation_fields (dict): Словарь, определяющий поля,
            доступные для перевода. В текущей модели
            поддерживается перевод поля 'name'.
        - offset (str): Строковое представление смещения временной
            зоны от UTC, например 'UTC +01:00'.
        - organisations (list[Organisation]): Список организаций,
            ассоциированных с данной временной зоной.
        - events (list[Event]): Список событий, ассоциированных
            с данной временной зоной.
        - users (User): Список пользователей, ассоциированных
            с данной временной зоной.
    """

    __tablename__ = "timezone"

    translation_fields = dict(name=mapped_column(String))

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    offset: Mapped[str] = mapped_column(String, nullable=False)

    organisations: Mapped[list["Organisation"]] = relationship(
        "Organisation", back_populates="timezone"
    )
    events: Mapped[list["Event"]] = relationship(
        "Event", back_populates="timezone"
    )
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="timezone"
    )

    def __str__(self) -> str:
        return f"{self.offset} {self.name}"
