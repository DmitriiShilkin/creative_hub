import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from fastapi_storages.integrations.sqlalchemy import FileType
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression, func

from constants.i18n import Languages
from models.base import Base
from models.m2m import EventOrganizers, EventSpeakers
from storages.s3_users import users_storage

from ..frilance import Proposal, ProposalStatus
from .favorite_user import FavoriteUsers

if TYPE_CHECKING:
    from models import (
        City,
        Education,
        Job,
        Link,
        Mentorship,
        Organisation,
        Project,
        ProposalTableConfig,
        SocialNetwork,
        UserExperience,
        UserSpecialization,
        VerificationCode,
    )
    from models.event import Event
    from models.user.private_site import PrivateSite


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vk_id: Mapped[Optional[int]] = mapped_column(
        Integer, unique=True, index=True, nullable=True
    )
    yandex_id: Mapped[Optional[int]] = mapped_column(
        Integer, unique=True, index=True, nullable=True
    )
    google_id: Mapped[Optional[str]] = mapped_column(
        String, unique=True, index=True, nullable=True
    )
    uid: Mapped[uuid.UUID] = mapped_column(
        UUID, unique=True, index=True, default=uuid.uuid4
    )
    first_name: Mapped[str]
    second_name: Mapped[str]
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    pending_email: Mapped[Optional[str]] = mapped_column(
        String, unique=True, nullable=True
    )
    birthday: Mapped[Optional[datetime]] = mapped_column(Date)
    photo: Mapped[Optional[FileType]] = mapped_column(
        FileType(storage=users_storage)
    )
    profile_cover: Mapped[Optional[FileType]] = mapped_column(
        FileType(storage=users_storage)
    )
    hashed_password: Mapped[str] = mapped_column(String, nullable=True)
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.false()
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.false()
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.false()
    )
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    last_visited_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    last_password_change_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), index=True
    )
    city_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("city.id", ondelete="SET NULL")
    )
    city: Mapped["City"] = relationship("City", back_populates="users")
    experience: Mapped[list["UserExperience"]] = relationship(
        "UserExperience", back_populates="user"
    )
    specialization: Mapped["UserSpecialization"] = relationship(
        "UserSpecialization", back_populates="user"
    )
    social_networks: Mapped[list["SocialNetwork"]] = relationship(
        "SocialNetwork", back_populates="user", cascade="all, delete-orphan"
    )
    private_site: Mapped["PrivateSite"] = relationship(
        "PrivateSite",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    links: Mapped[list["Link"]] = relationship(
        "Link", back_populates="user", cascade="all, delete-orphan"
    )
    email_verification: Mapped["VerificationCode"] = relationship(
        "VerificationCode",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    favorite_users = relationship(
        "User",
        secondary=FavoriteUsers.__table__,
        primaryjoin=id == FavoriteUsers.user_id,
        secondaryjoin=id == FavoriteUsers.favorite_user_id,
    )
    authored_projects: Mapped[list["Project"]] = relationship(
        "Project", back_populates="author"
    )
    coauthored_projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="coauthors",
        secondary="projects_coauthors",
    )
    mentorship: Mapped["Mentorship"] = relationship(
        "Mentorship",
        back_populates="user",
    )
    created_organisations: Mapped["Organisation"] = relationship(
        "Organisation", back_populates="creator"
    )

    education: Mapped[list["Education"]] = relationship(
        "Education",
        back_populates="user",
    )

    authored_jobs: Mapped["Job"] = relationship(
        "Job",
        back_populates="author",
    )
    proposals: Mapped[list["Proposal"]] = relationship(
        "Proposal", back_populates="user", foreign_keys="[Proposal.user_id]"
    )
    updated_proposals: Mapped[list["Proposal"]] = relationship(
        "Proposal",
        back_populates="updated_by",
        foreign_keys="[Proposal.updated_by_id]",
    )
    proposal_statuses: Mapped["ProposalStatus"] = relationship(
        "ProposalStatus", back_populates="user"
    )
    proposal_table_config: Mapped["ProposalTableConfig"] = relationship(
        "ProposalTableConfig", back_populates="user"
    )
    language: Mapped[Optional[Languages]] = mapped_column(
        ENUM(Languages, create_type=False)
    )

    organized_events: Mapped[list["Event"]] = relationship(
        "Event",
        secondary=EventOrganizers.__table__,
        back_populates="organizers",
    )
    speaking_events: Mapped[list["Event"]] = relationship(
        "Event",
        secondary=EventSpeakers.__table__,
        back_populates="speakers",
    )
    created_events: Mapped[list["Event"]] = relationship(
        "Event", back_populates="creator"
    )

    @property
    def fullname(self) -> str:
        return f"{self.second_name} {self.first_name}"

    def __str__(self) -> str:
        return f"{self.id} - {self.fullname}"
