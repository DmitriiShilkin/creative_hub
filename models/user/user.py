import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from fastapi_storages.integrations.sqlalchemy import FileType
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, ENUM, JSONB, UUID, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression, func

from constants.contacts import ContactInfo
from constants.i18n import Languages
from models.base import Base
from models.m2m import (
    CalendarEventUsers,
    EventOrganizers,
    EventSpeakers,
    ProjectLikes,
)
from constants.completeness import UserProfileCompleteness
from storages.s3_users import users_storage

if TYPE_CHECKING:
    from models.event_participants import EventParticipants
    from models import (
        CalendarEvent,
        CalendarEventComment,
        City,
        Education,
        Event,
        EventView,
        Favorite,
        Job,
        JobView,
        Link,
        Mentorship,
        Organisation,
        PrivateSite,
        Project,
        ProjectView,
        Proposal,
        ProposalStatus,
        ProposalTableConfig,
        TextDocument,
        Timezone,
        UserExperience,
        UserSpecialization,
        VerificationCode,
        Status,
    )


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
    schedule: Mapped[Optional[dict]] = mapped_column(JSONB, default=JSONB.NULL)
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
    external_link_permission: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.false()
    )
    city_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("city.id", ondelete="SET NULL")
    )
    city: Mapped["City"] = relationship("City", back_populates="users")
    experience: Mapped[list["UserExperience"]] = relationship(
        "UserExperience", back_populates="user"
    )
    timezone_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("timezone.id"), nullable=True
    )
    timezone: Mapped["Timezone"] = relationship(
        "Timezone", back_populates="users"
    )
    active_organisation_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("organisation.id", name="user_active_organisation"),
        nullable=True,
    )
    active_organisation: Mapped[Optional["Organisation"]] = relationship(
        "Organisation",
        back_populates="active_organisation_users",
        foreign_keys=active_organisation_id,
        post_update=True,
    )
    specialization: Mapped["UserSpecialization"] = relationship(
        "UserSpecialization", back_populates="user"
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
    contact_info: Mapped[ContactInfo] = mapped_column(JSON, default={})
    email_verification: Mapped["VerificationCode"] = relationship(
        "VerificationCode",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite",
        back_populates="user",
        foreign_keys="[Favorite.user_id]",
    )
    profile_completeness: Mapped[UserProfileCompleteness] = mapped_column(
        JSON(), default={}
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
    created_organisations: Mapped[list["Organisation"]] = relationship(
        "Organisation",
        back_populates="creator",
        foreign_keys="Organisation.creator_id",
    )
    education: Mapped[list["Education"]] = relationship(
        "Education",
        back_populates="user",
    )
    authored_jobs: Mapped[list["Job"]] = relationship(
        "Job",
        back_populates="author",
    )
    coauthored_jobs: Mapped[list["Job"]] = relationship(
        "Job",
        back_populates="coauthors",
        secondary="job_coauthors",
    )
    proposals: Mapped[list["Proposal"]] = relationship(
        "Proposal", back_populates="user", foreign_keys="[Proposal.user_id]"
    )
    job_views: Mapped[list["JobView"]] = relationship(
        "JobView",
        back_populates="user",
    )
    project_views: Mapped[list["ProjectView"]] = relationship(
        "ProjectView",
        back_populates="user",
    )
    event_views: Mapped[list["EventView"]] = relationship(
        "EventView", back_populates="user"
    )
    updated_proposals: Mapped[list["Proposal"]] = relationship(
        "Proposal",
        back_populates="updated_by",
        foreign_keys="[Proposal.updated_by_id]",
    )
    proposal_statuses: Mapped[list["ProposalStatus"]] = relationship(
        "ProposalStatus", back_populates="user"
    )
    statuses: Mapped[list["Status"]] = relationship(
        "Status", back_populates="user"
    )
    proposal_table_config: Mapped[list["ProposalTableConfig"]] = relationship(
        "ProposalTableConfig", back_populates="user"
    )
    main_language: Mapped[Optional[Languages]] = mapped_column(
        ENUM(Languages, create_type=False)
    )
    languages: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(String()),
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
    events_attending: Mapped[list["EventParticipants"]] = relationship(
        "EventParticipants",
        back_populates="user",
        foreign_keys="[EventParticipants.user_id]",
        cascade="all, delete",
        passive_deletes=True,
    )

    created_events: Mapped[list["Event"]] = relationship(
        "Event",
        back_populates="creator",
        foreign_keys="[Event.creator_id]",
    )
    created_text_documents: Mapped[list["TextDocument"]] = relationship(
        "TextDocument", back_populates="author"
    )

    calendar_events_participant: Mapped[list["CalendarEvent"]] = relationship(
        "CalendarEvent",
        secondary=CalendarEventUsers.__table__,
        back_populates="participants",
    )
    calendar_events_organizer: Mapped[list["CalendarEvent"]] = relationship(
        "CalendarEvent",
        back_populates="organizer",
    )
    calendar_comments: Mapped[list["CalendarEventComment"]] = relationship(
        "CalendarEventComment",
        back_populates="author",
    )
    liked_projects: Mapped[list["Project"]] = relationship(
        "Project",
        secondary=ProjectLikes.__table__,
        back_populates="users_likes",
    )
    updated_events_attendance: Mapped[list["EventParticipants"]] = (
        relationship(
            "EventParticipants",
            back_populates="updated_by",
            foreign_keys="[EventParticipants.updated_by_id]",
        )
    )
    sections: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(String()), nullable=True
    )

    @property
    def fullname(self) -> str:
        return f"{self.second_name} {self.first_name}"

    def __str__(self) -> str:
        return f"{self.id} - {self.fullname}"
