from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression

from constants.education import EducationType
from models.base import Base

if TYPE_CHECKING:
    from models.city import City
    from models.user import EducationCertificateFile, User


class Education(Base):
    """
    Класс образовательной информации пользователя.

     # Attrs:
        - id (int): Уникальный идентификатор записи образования.
        - type (EducationType): Тип образования
        - name (str): Название учебного заведения.
        - department (str): Название факультета или кафедры.
        - start_month (Month): Месяц начала обучения
        - start_year (int): Год начала обучения.
        - end_month (Month, optional): Месяц окончания обучения
        - end_year (int, optional): Год окончания обучения, может быть None.
        - is_current (bool): Флаг текущего обучения.
        - certificates (list[EducationCertificateFile]): Список сертификатов
        - city (City, optional): Город, связанный с учебным заведением.
        - city_id (int, optional): Внешний ключ для связи с городом.
        - user_id (int): Внешний ключ для связи с пользователем.
        - user (User): Связь с пользовательским профилем.
    """

    __tablename__ = "education"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    type: Mapped[EducationType] = mapped_column(
        ENUM(EducationType, create_type=False)
    )
    name: Mapped[str]
    department: Mapped[str]

    start_month: Mapped[int]
    start_year: Mapped[int]
    end_month: Mapped[Optional[int]]
    end_year: Mapped[Optional[int]]
    is_current: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.false()
    )
    certificates: Mapped[list["EducationCertificateFile"]] = relationship(
        "EducationCertificateFile",
        back_populates="education",
    )
    city: Mapped[Optional["City"]] = relationship(
        "City", back_populates="educations"
    )

    city_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("city.id"), nullable=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE")
    )
    user: Mapped["User"] = relationship("User", back_populates="education")

    def __str__(self) -> str:
        return f"{self.id} - {self.user}- {self.name}"
