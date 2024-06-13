from datetime import date, datetime
from typing import Optional
from uuid import UUID

from email_validator import validate_email
from pydantic import BaseModel, PositiveInt, model_validator
from pydantic.class_validators import validator

from constants.i18n import Languages
from schemas.city import CityWithCountryResponse
from schemas.common import PasswordBase
from schemas.email_validator import EmailStrLower
from schemas.social_network import SocialNetworkResponse
from schemas.specialization import SpecializationWithDirectionResponse
from schemas.timezone import TimezoneResponse


class UserBase(BaseModel):
    first_name: str
    second_name: str
    email: EmailStrLower

    class Config:
        from_attributes = True

    @validator("email")
    def email_check(cls, v: EmailStrLower) -> EmailStrLower:
        email_info = validate_email(v, check_deliverability=True)
        email = email_info.normalized
        return email


class UserCreate(PasswordBase, UserBase):
    pass


class UserCreateDB(UserBase):
    uid: UUID
    username: str
    hashed_password: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    username: Optional[str] = None
    birthday: Optional[date] = None
    language: Optional[Languages] = None
    city_id: Optional[PositiveInt] = None
    timezone_id: Optional[PositiveInt] = None


class UserSimpleResponse(UserBase):
    uid: UUID
    username: Optional[str] = None
    photo: Optional[str] = None
    last_visited_at: Optional[datetime] = None
    profile_cover: Optional[str] = None


class UserResponse(UserSimpleResponse):
    language: Optional[Languages] = None
    city: Optional[CityWithCountryResponse] = None
    birthday: Optional[datetime] = None
    timezone: Optional[TimezoneResponse] = None


class UserDetailResponse(UserSimpleResponse):
    is_expert: bool

    @model_validator(mode="before")
    def is_expert_validator(self):
        self.is_expert = bool(self.mentorship)
        return self


class UserProfileResponse(UserDetailResponse):
    profile_cover: Optional[str] = None
    registered_at: datetime
    birthday: Optional[date] = None
    last_password_change_at: Optional[datetime] = None


class UserPhotosResponse(BaseModel):
    photo: Optional[str] = None
    profile_cover: Optional[str] = None


class UserParticipantResponse(UserBase):
    id: int
    photo: Optional[str] = None
    social_networks: list[SocialNetworkResponse]
    specializations: list[SpecializationWithDirectionResponse] = []

    class Config:
        from_attributes = True


class UserEventResponse(BaseModel):
    first_name: str
    second_name: str
    photo: Optional[str] = None


class UserCalendarResponse(BaseModel):
    uid: UUID
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    username: Optional[str] = None
    photo: Optional[str] = None
