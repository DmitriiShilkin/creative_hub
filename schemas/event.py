from datetime import datetime, UTC
from typing import List, Optional, Self, Any
from uuid import UUID

from fastapi import UploadFile
from fastapi.exceptions import RequestValidationError
from pydantic import (
    BaseModel,
    Field,
    PositiveInt,
    ValidationError,
    ValidationInfo,
    field_validator,
    model_validator,
    validator,
)

from constants.event import EventType, RegistrationEndType, ReminderUnits
from constants.i18n import EventLanguage
from models import Event
from schemas.city import CityWithCountryResponse
from schemas.mixins import ExplicitFieldsParseJsonMixin, ParseFromJsonMixin
from schemas.organisation.organisation import OrganisationShortResponse
from schemas.specialization import SpecializationResponse
from schemas.timezone import TimezoneCreate, TimezoneSimpleResponse
from schemas.user.contact_person import ContactPersonResponse
from schemas.user.user import UserEventResponse, UserParticipantResponse


class EventPlacesBase(BaseModel):
    address: str
    place_name: str


class EventValidationMixin(BaseModel):
    start_datetime: datetime
    end_datetime: datetime
    registration_end_datetime: Optional[datetime]
    registration_end_type: Optional[RegistrationEndType]
    is_draft: bool = True
    places: Optional[List[EventPlacesBase]]
    is_online: Optional[bool]

    @model_validator(mode="after")
    def validate_job_condition(self, values: ValidationInfo) -> Self:
        if "title" not in values.config or values.config["title"] is None:
            return self

        if not self.is_draft and values.config["title"] in [
            EventCreateDraft.__name__,
            EventUpdate.__name__,
        ]:
            try:
                EventCreate.model_validate(self, strict=True)
            except ValidationError as ex:
                raise RequestValidationError(ex.errors()) from ex
        return self

    @field_validator("start_datetime")
    @classmethod
    def validate_start_datetime(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        date_now = datetime.now(tz=UTC)
        if value < date_now:
            err = "Value of `start_datetime` should not be in the past"
            raise RequestValidationError(err)
        return value

    @model_validator(mode="after")
    def validate_dates(self) -> "EventCreateDraft":
        start_dt = (
            self.start_datetime.replace(tzinfo=UTC)
            if self.start_datetime
            else None
        )
        end_dt = (
            self.end_datetime.replace(tzinfo=UTC)
            if self.end_datetime
            else None
        )
        reg_end_dt = (
            self.registration_end_datetime.replace(tzinfo=UTC)
            if self.registration_end_datetime
            else None
        )

        if self.end_datetime is None or self.start_datetime is None:
            err = "Start datetime or end datetime cannot be None."
            raise RequestValidationError(err)
        if end_dt < start_dt:
            err = (
                f"The value of `end_datetime` "
                f"({end_dt.isoformat()}) cannot be earlier"
                f" than `start_datetime` ({start_dt.isoformat()})."
            )
            raise RequestValidationError(err)

        if reg_end_dt and reg_end_dt > end_dt:
            err = (
                "The value of `registration_end_datetime`"
                f"({reg_end_dt.isoformat()})"
                " cannot be later than `end_datetime`"
                f"({end_dt.isoformat()})."
            )
            raise RequestValidationError(err)

        if (
            self.registration_end_type
            == RegistrationEndType.CUSTOM_BEFORE_EVENT
            and not self.registration_end_datetime
        ):
            err = (
                "If the `registration_end_type` is `CUSTOM_BEFORE_EVENT`,"
                " `registration_end_datetime` must be NOT None."
            )
            raise RequestValidationError(err)

        if (
            self.registration_end_type
            == RegistrationEndType.CUSTOM_BEFORE_EVENT
            and reg_end_dt > start_dt
        ):
            err = (
                "If the `registration_end_type` is `CUSTOM_BEFORE_EVENT`, "
                "the value of `registration_end_datetime`"
                f"({reg_end_dt}) "
                "cannot be later than `start_datetime`"
                f"({start_dt})."
            )
            raise RequestValidationError(err)

        if (
            self.registration_end_type == RegistrationEndType.AT_EVENT_START
            and self.registration_end_datetime is not None
        ):
            err = (
                "If the `registration_end_type` is `AT_EVENT_START`,"
                " `registration_end_datetime` must be None."
            )
            raise RequestValidationError(err)

        if self.is_online and self.places:
            err = "If the `is_online` is `ONLINE`, `places` must be None."
            raise RequestValidationError(err)

        return self


class EventReminder(BaseModel):
    reminder_before_event: PositiveInt
    reminder_unit: ReminderUnits
    reminder_time: str

    @validator("reminder_before_event")
    @classmethod
    def validate_reminder_before_event(cls, value: int) -> int:
        if value:
            if value < 0:
                err = (
                    "The value of `reminder_before_event`"
                    "cannot be a negative number"
                )
                raise RequestValidationError(err)
            return value


class BaseEvent(BaseModel):
    title: str
    description: Optional[str]
    language: Optional[EventLanguage]
    extra_languages: List[EventLanguage]
    is_free: Optional[bool]
    is_online: Optional[bool]
    start_datetime: Optional[datetime]
    end_datetime: Optional[datetime]
    registration_end_datetime: Optional[datetime]
    registration_end_type: Optional[RegistrationEndType]
    reminders: Optional[List[EventReminder]]
    is_draft: bool = True

    class Config:
        from_attributes = True


class EventCreate(EventValidationMixin, BaseEvent):
    description: Optional[str] = ""
    event_type: EventType
    language: EventLanguage
    extra_languages: List[EventLanguage]
    is_free: bool
    is_online: bool
    timezone_id: int
    city_id: Optional[PositiveInt] = None
    places: Optional[List[EventPlacesBase]] = Field(default_factory=list)
    online_links: Optional[List[str]] = Field(default_factory=list)
    organizers_uids: Optional[List[UUID]] = Field(
        min_length=1, default_factory=list
    )
    speakers_uids: Optional[List[UUID]] = Field(default_factory=list)
    specializations_ids: Optional[List[PositiveInt]] = Field(
        default_factory=list
    )
    organisations_ids: Optional[List[PositiveInt]] = Field(
        default_factory=list
    )
    reminders: Optional[List[EventReminder]] = Field(default_factory=list)


class EventUpdate(ExplicitFieldsParseJsonMixin):
    title: Optional[str] = None
    description: Optional[str] = ""
    language: Optional[EventLanguage] = None
    extra_languages: Optional[List[EventLanguage]] = None
    event_type: Optional[EventType] = None
    is_free: Optional[bool] = None
    is_online: Optional[bool] = None
    timezone: Optional[TimezoneCreate] = None
    city_id: Optional[PositiveInt] = None
    places: Optional[List[EventPlacesBase]] = None
    online_links: Optional[List[str]] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    registration_end_datetime: Optional[datetime] = None
    registration_end_type: Optional[RegistrationEndType] = None
    organizers_uids: Optional[List[UUID]] = None
    speakers_uids: Optional[List[UUID]] = None
    specializations_ids: Optional[List[PositiveInt]] = None
    organisations_ids: Optional[List[PositiveInt]] = None
    reminders: Optional[List[EventReminder]] = Field(default_factory=list)
    is_draft: Optional[bool] = None


class EventCreateDraft(ParseFromJsonMixin):
    title: str
    description: Optional[str] = ""
    language: Optional[EventLanguage] = None
    extra_languages: List[EventLanguage]
    event_type: Optional[EventType] = None
    is_free: Optional[bool] = None
    is_online: Optional[bool] = None
    timezone: Optional[TimezoneCreate] = None
    city_id: Optional[PositiveInt] = None
    places: Optional[List[EventPlacesBase]] = Field(default_factory=list)
    online_links: Optional[List[str]] = Field(default_factory=list)
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    registration_end_datetime: Optional[datetime] = None
    registration_end_type: Optional[RegistrationEndType] = None
    organizers_uids: List[UUID] = Field(default_factory=list)
    speakers_uids: Optional[List[UUID]] = Field(default_factory=list)
    specializations_ids: Optional[List[PositiveInt]] = Field(
        default_factory=list
    )
    organisations_ids: Optional[List[PositiveInt]] = Field(
        default_factory=list
    )
    reminders: Optional[List[EventReminder]] = Field(default_factory=list)
    is_draft: bool = True


class EventCreateDB(BaseModel):
    creator_id: Optional[int] = None
    photo: Optional[UploadFile] = None
    event_cover: Optional[UploadFile] = None
    title: str
    description: Optional[str] = ""
    language: Optional[EventLanguage] = None
    extra_languages: List[EventLanguage]
    event_type: Optional[EventType] = None
    is_free: Optional[bool] = True
    is_online: Optional[bool] = False
    timezone_id: Optional[PositiveInt] = None
    city_id: Optional[PositiveInt] = None
    places: Optional[List[EventPlacesBase]] = None
    online_links: Optional[List[str]] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    registration_end_datetime: Optional[datetime] = None
    registration_end_type: Optional[RegistrationEndType] = None
    reminders: Optional[List[EventReminder]] = None
    is_draft: bool = True
    is_archived: bool = False


class EventUpdateDB(BaseModel):
    creator_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    language: Optional[EventLanguage] = None
    extra_languages: Optional[List[EventLanguage]] = None
    event_type: Optional[EventType] = None
    is_free: Optional[bool] = None
    is_online: Optional[bool] = None
    timezone_id: Optional[PositiveInt] = None
    city_id: Optional[PositiveInt] = None
    places: Optional[List[EventPlacesBase]] = None
    online_links: Optional[List[str]] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    registration_end_datetime: Optional[datetime] = None
    registration_end_type: Optional[RegistrationEndType] = None
    reminders: Optional[List[EventReminder]] = None
    is_draft: Optional[bool] = None


class EventSimpleResponse(BaseEvent):
    id: int
    photo: Optional[str] = None
    event_cover: Optional[str] = None
    event_type: Optional[EventType] = None
    places: Optional[List[EventPlacesBase]] = []
    online_links: Optional[List[str]]


class EventResponse(EventSimpleResponse):
    specializations: List[SpecializationResponse]
    city: Optional[CityWithCountryResponse]
    timezone: Optional[TimezoneSimpleResponse]
    organizers: List[UserParticipantResponse]
    speakers: List[UserParticipantResponse]
    contact_persons: List[ContactPersonResponse]
    organisations: List[OrganisationShortResponse]
    participants: List[UserEventResponse]
    creator: UserEventResponse
    is_draft: bool
    is_archived: Optional[bool] = None
    created_at: datetime


class EventWithCountersResponse(EventResponse):
    new_participants_count: Optional[int] = None
    participants_count: Optional[int] = None
    browsing_now: Optional[int] = None
    views: Optional[int] = None
    is_viewed_by_current_user: Optional[bool] = None

    class Config:
        arbitrary_types_allowed = True

    @model_validator(mode="before")
    def schema_nested_parser(self) -> Any:
        if isinstance(self, Event):
            return self
        data = self["Event"].__dict__
        data["new_participants_count"] = self["new_participants_count"]
        data["participants_count"] = self["participants_count"]
        data["views"] = self["views"]
        if "is_viewed_by_current_user" in self:
            data["is_viewed_by_current_user"] = self[
                "is_viewed_by_current_user"
            ]
        return data

    @model_validator(mode="before")
    def add_context_data(self, values: ValidationInfo, **kwargs) -> Self:
        if values.context:
            if "new_participants_count" in values.context:
                self.new_participants_count = values.context[
                    "new_participants_count"
                ]
            if "participants_count" in values.context:
                self.participants_count = values.context["participants_count"]
            if "views" in values.context:
                self.views = values.context["views"]
            if "browsing_now" in values.context:
                self.browsing_now = values.context["browsing_now"]
        return self


class EventTypesResponse(BaseModel):
    types: List[EventType]


class EventLanguagesResponse(BaseModel):
    languages: List[EventLanguage]
