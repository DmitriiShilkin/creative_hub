import logging
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression

from constants.finance import Currency, PaymentPer
from constants.i18n import Languages
from models.base import Base
from models.m2m import JobCoauthors, JobContactPersons, JobSpecializations

if TYPE_CHECKING:
    from models import City, Favorite, Proposal, ProposalTableConfig
    from models.contact_person import ContactPerson
    from models.media_file import MediaFile
    from models.user import User
    from models.user.specialization import Specialization
    from models.views import View


class Job(Base):
    __tablename__ = "job"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str]
    description: Mapped[str] = mapped_column(Text)

    author_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE")
    )
    accepted_languages: Mapped[list[Languages]] = mapped_column(
        ARRAY(ENUM(Languages, create_type=False))
    )
    budget: Mapped[Optional[int]]
    currency: Mapped[Optional[Currency]] = mapped_column(
        ENUM(Currency, create_type=False)
    )
    payment_per: Mapped[Optional[PaymentPer]] = mapped_column(
        ENUM(PaymentPer, create_type=False)
    )
    is_negotiable_price: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.false()
    )
    is_remote: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.true()
    )
    deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    adult_content: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.false()
    )
    for_verified_users: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.false()
    )
    is_draft: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.true()
    )
    is_archived: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.false()
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
    city_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("city.id", ondelete="CASCADE")
    )
    city: Mapped["City"] = relationship(
        "City",
        back_populates="jobs",
    )
    author: Mapped["User"] = relationship(
        "User", back_populates="authored_jobs"
    )
    coauthors: Mapped[list["User"]] = relationship(
        "User",
        back_populates="coauthored_jobs",
        secondary=JobCoauthors.__table__,
    )
    specializations: Mapped[list["Specialization"]] = relationship(
        "Specialization",
        back_populates="jobs",
        secondary=JobSpecializations.__table__,
    )
    contact_persons: Mapped[list["ContactPerson"]] = relationship(
        "ContactPerson",
        back_populates="jobs",
        secondary=JobContactPersons.__table__,
    )
    proposals: Mapped[list["Proposal"]] = relationship(
        "Proposal",
        back_populates="job",
        cascade="all, delete",
        passive_deletes=True,
    )
    view_records: Mapped[list["View"]] = relationship(
        "View",
        back_populates="job",
        cascade="all, delete",
        passive_deletes=True,
    )
    files: Mapped[list["MediaFile"]] = relationship(
        "MediaFile",
        back_populates="job",
        cascade="all, delete",
        passive_deletes=True,
    )
    proposal_table_config: Mapped[list["ProposalTableConfig"]] = relationship(
        "ProposalTableConfig",
        back_populates="job",
        cascade="all, delete",
        passive_deletes=True,
    )
    favorites: Mapped[List["Favorite"]] = relationship(
        "Favorite", back_populates="job"
    )

    @property
    def filenames(self) -> list[str]:
        try:
            return [f.file for f in self.files]
        except Exception as ex:
            logging.exception(ex)
            return []

    def __str__(self):
        return f"{self.id}: {self.name}"
