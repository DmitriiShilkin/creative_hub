from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.city import City

    from .user import User


class UserExperience(Base):
    """
    Модель опыта работы пользователя.

    # Attrs:
        - id: (int)
        - company_name: str - Название компании,
          в которой работал пользователя.
        - job_title: str - Название должности.
        - start_month: int - Месяц начала работы.
        - start_year: int - Год начала работы.
        - end_month: int - Месяц окончания работы.
        - end_year: int - Год окончания работы.
        - still_working: bool - Работает ли пользователь на данный момент.
        - city_id: int - Идентификатор города, в котором работал пользователь.
        - city: City - Объект города, в котором работал пользователь.
        - user_id: int (FK) - Индентификатор пользователя.
        - user: User - Объект пользователя.
    """

    __tablename__ = "user_experience"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    company_name: Mapped[str]
    job_title: Mapped[str]
    start_month: Mapped[int]
    start_year: Mapped[int]
    end_month: Mapped[Optional[int]]
    end_year: Mapped[Optional[int]]
    still_working: Mapped[bool] = mapped_column(server_default="false")
    city_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "city.id",
            ondelete="CASCADE",
        ),
    )
    city: Mapped["City"] = relationship(
        "City",
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(
            "user.id",
            ondelete="CASCADE",
        ),
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="experience",
    )
