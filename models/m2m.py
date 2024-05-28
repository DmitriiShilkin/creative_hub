from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class UsersSpecializations(Base):
    __tablename__ = "users_specializations"

    user_specialization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user_specialization.id", ondelete="CASCADE"),
        primary_key=True,
    )
    specialization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("specialization.id", ondelete="CASCADE"),
        primary_key=True,
    )


class UserSpecializationKeywords(Base):
    __tablename__ = "user_specialization_keywords"

    user_specialization_id: Mapped[int] = mapped_column(
        ForeignKey("user_specialization.id", ondelete="CASCADE"),
        primary_key=True,
    )
    keyword_id: Mapped[int] = mapped_column(
        ForeignKey("keyword.id", ondelete="CASCADE"),
        primary_key=True,
    )


class ProjectsCoauthors(Base):
    __tablename__ = "projects_coauthors"

    project_id: Mapped[int] = mapped_column(
        ForeignKey("project.id", ondelete="CASCADE"),
        primary_key=True,
    )
    coauthor_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    )


class ProjectsKeywords(Base):
    __tablename__ = "projects_keywords"

    project_id: Mapped[int] = mapped_column(
        ForeignKey("project.id", ondelete="CASCADE"),
        primary_key=True,
    )
    keyword_id: Mapped[int] = mapped_column(
        ForeignKey("keyword.id", ondelete="CASCADE"),
        primary_key=True,
    )


class EventSpecializations(Base):
    __tablename__ = "event_specializations"

    event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("event.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    specialization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("specialization.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )


class MentorshipSpecializations(Base):
    __tablename__ = "mentorship_specializations"

    mentorship_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("mentorship.id", ondelete="CASCADE"),
        primary_key=True,
    )
    specialization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("specialization.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )


class EventOrganizers(Base):
    __tablename__ = "event_organizers"

    event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("event.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )


class EventSpeakers(Base):
    __tablename__ = "event_speakers"

    event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("event.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )


class MentorshipKeywords(Base):
    __tablename__ = "mentorship_keywords"

    mentorship_id: Mapped[int] = mapped_column(
        ForeignKey("mentorship.id", ondelete="CASCADE"),
        primary_key=True,
    )
    keyword_id: Mapped[int] = mapped_column(
        ForeignKey("keyword.id", ondelete="CASCADE"),
        primary_key=True,
    )


class MentorshipDemands(Base):
    __tablename__ = "mentorship_demands"

    mentorship_id: Mapped[int] = mapped_column(
        ForeignKey("mentorship.id", ondelete="CASCADE"),
        primary_key=True,
    )
    demand_id: Mapped[int] = mapped_column(
        ForeignKey("mentorship_demand.id", ondelete="CASCADE"),
        primary_key=True,
    )


class JobSpecializations(Base):
    __tablename__ = "job_specializations"

    job_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("job.id", ondelete="CASCADE"),
        primary_key=True,
    )
    specialization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("specialization.id", ondelete="CASCADE"),
        primary_key=True,
    )


class JobContactPersons(Base):
    __tablename__ = "job_contact_persons"

    job_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("job.id", ondelete="CASCADE"),
        primary_key=True,
    )
    contact_person_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("contact_person.id", ondelete="CASCADE"),
        primary_key=True,
    )


class EventContactPerson(Base):
    __tablename__ = "event_contact_persons"

    event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("event.id", ondelete="CASCADE"),
        primary_key=True,
    )
    contact_person_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("contact_person.id", ondelete="CASCADE"),
        primary_key=True,
    )


class OrganisationSpecializations(Base):
    __tablename__ = "organisation_specializations"

    organisation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("organisation.id", ondelete="CASCADE"),
        primary_key=True,
    )
    specialization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("specialization.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )


class OrganisationKeywords(Base):
    __tablename__ = "Organisations_keywords"

    organisation_id: Mapped[int] = mapped_column(
        ForeignKey("organisation.id", ondelete="CASCADE"),
        primary_key=True,
    )
    keyword_id: Mapped[int] = mapped_column(
        ForeignKey("keyword.id", ondelete="CASCADE"),
        primary_key=True,
    )


class OrganisationContactPersons(Base):
    __tablename__ = "organisation_contact_persons"

    organisation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("organisation.id", ondelete="CASCADE"),
        primary_key=True,
    )
    contact_person_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("contact_person.id", ondelete="CASCADE"),
        primary_key=True,
    )


class DirectionOrganisations(Base):
    __tablename__ = "direction_organisations"

    organisation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("organisation.id", ondelete="CASCADE"),
        primary_key=True,
    )
    direction_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("direction.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )


class MultipleProposalChoiceAnswer(Base):
    __tablename__ = "multiple_proposal_choice_answer"

    proposal_choice_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("proposal_choice.id", ondelete="CASCADE"),
        primary_key=True,
    )
    multiple_answer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("multiple_choice_answer.id", ondelete="CASCADE"),
        primary_key=True,
    )


class EventsOrganisations(Base):
    __tablename__ = "events_organisations"

    event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("event.id", ondelete="CASCADE"),
        primary_key=True,
    )
    organisation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("organisation.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )


class CalendarEventUsers(Base):
    """
    Модель участников события m2m
    (раздел календарь)

    ## Attrs
        - event_id : int - идентификатор события
        - user_id : int - идентификатор пользователя (участника)
    """

    __tablename__ = "calendar_event_users"

    event_id: Mapped[int] = mapped_column(
        ForeignKey("calendar_event.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    )
