from datetime import datetime
from typing import List, Optional, Self, Union
from uuid import UUID

from fastapi.exceptions import RequestValidationError
from pydantic import (
    BaseModel,
    Field,
    PositiveInt,
    ValidationError,
    model_validator,
)
from pydantic_core.core_schema import ValidationInfo

from constants.finance import Currency, PaymentPer
from constants.i18n import Languages
from models import Job
from schemas.city import CityWithCountryResponse
from schemas.common import FileResponse
from schemas.frilance.proposals import ProposalIdResponse, ProposalResponse
from schemas.mixins import ParseFromJsonMixin
from schemas.specialization import SpecializationWithDirectionResponse
from schemas.user.contact_person import ContactPersonResponse
from schemas.user.user import UserSimpleResponse


class ModificationMixin(BaseModel):
    specialization_ids: Optional[List[PositiveInt]] = None
    accepted_languages: Optional[List[Languages]] = None
    budget: Optional[PositiveInt] = None
    currency: Optional[Currency] = None
    payment_per: Optional[PaymentPer] = None
    is_negotiable_price: Optional[bool] = False
    is_draft: bool = True
    city_id: Optional[PositiveInt]
    is_remote: bool

    @model_validator(mode="after")
    def validate_job_condition(self, values: ValidationInfo) -> Self:
        if (
            not self.is_draft
            and "title" in values.config
            and values.config["title"]
            in [JobCreateDraft.__name__, JobUpdate.__name__]
        ):
            try:
                JobCreate.model_validate(self, strict=True)
            except ValidationError as ex:
                raise RequestValidationError(ex.errors())
        if self.is_negotiable_price and (
            self.budget or self.currency or self.payment_per
        ):
            raise RequestValidationError(
                "Choose only `is_negotiable_price` or "
                "define [`budget`, `currency`, `payment_per`]"
            )
        return self

    @model_validator(mode="after")
    def validate_city_and_is_remote(self, values: ValidationInfo) -> Self:
        if self.is_remote and self.city_id:
            raise RequestValidationError(
                "It's not allowed to simultaneously"
                " set is_remote = True and city_id"
            )
        return self


class JobBase(BaseModel):
    name: str
    description: str
    accepted_languages: List[Languages]
    adult_content: bool
    for_verified_users: bool

    class Config:
        from_attributes = True


class JobCreateDraft(ParseFromJsonMixin, ModificationMixin):
    name: str
    description: Optional[str] = ""
    deadline: Optional[datetime] = None
    adult_content: Optional[bool] = False
    for_verified_users: Optional[bool] = False
    accepted_languages: Optional[List[Languages]]
    specialization_ids: Optional[List[PositiveInt]]
    author_uid: Optional[UUID] = None
    city_id: Optional[PositiveInt] = None
    is_remote: bool = True
    coauthors_uids: Optional[List[UUID]] = Field(default_factory=list)


class JobCreate(JobBase, ModificationMixin):
    accepted_languages: Optional[List[Languages]] = Field(min_length=1)
    specialization_ids: Optional[List[PositiveInt]] = Field(min_length=1)
    author_uid: UUID


class JobCreateDB(BaseModel):
    name: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    adult_content: Optional[bool] = None
    for_verified_users: Optional[bool] = None
    accepted_languages: Optional[Union[List[Languages], str]] = []
    author_id: Optional[int]
    budget: Optional[PositiveInt] = None
    currency: Optional[Currency] = None
    payment_per: Optional[PaymentPer] = None
    is_negotiable_price: Optional[bool] = False
    is_draft: bool = True
    city_id: Optional[PositiveInt] = None
    is_remote: bool = True


class JobUpdate(ModificationMixin, ParseFromJsonMixin):
    name: Optional[str] = None
    description: str | None = None
    deadline: Optional[datetime] = None
    adult_content: Optional[bool] = False
    for_verified_users: Optional[bool] = False
    accepted_languages: Optional[List[Languages]]
    specialization_ids: Optional[List[PositiveInt]]
    author_uid: Optional[UUID] = None
    is_archived: Optional[bool] = False
    files_ids_to_delete: Optional[List[PositiveInt]] = None
    city_id: Optional[PositiveInt] = None
    coauthors_uids: Optional[List[UUID]] = Field(default_factory=list)
    is_remote: Optional[bool] = None


class JobUpdateDB(BaseModel):
    name: str
    description: Optional[str]
    deadline: Optional[datetime]
    adult_content: Optional[bool]
    for_verified_users: Optional[bool]
    accepted_languages: Optional[List[Languages]]
    author_id: Optional[int] = None
    budget: Optional[PositiveInt]
    currency: Optional[Currency]
    payment_per: Optional[PaymentPer]
    is_negotiable_price: Optional[bool]
    is_draft: Optional[bool]
    is_archived: Optional[bool]
    city_id: Optional[PositiveInt]
    is_remote: Optional[bool]


class JobSimpleResponse(JobBase):
    id: int
    budget: Optional[int]
    currency: Optional[Currency]
    payment_per: Optional[PaymentPer]
    is_negotiable_price: bool
    deadline: Optional[datetime]
    created_at: datetime
    is_remote: bool


class JobResponse(JobSimpleResponse):
    specializations: List[SpecializationWithDirectionResponse]
    author: UserSimpleResponse
    contact_persons: List[ContactPersonResponse]
    proposals_count: int
    views: int
    new_proposals_count: int
    is_viewed_by_current_user: Optional[bool] = None
    city: Optional[CityWithCountryResponse]
    browsing_now: Optional[int] = None

    @model_validator(mode="before")
    def schema_nested_parser(self, values):
        if isinstance(self, Job):
            return self
        data = self["Job"].__dict__
        if values.context is not None:
            new_proposals_count = values.context.get("new_proposals_count", 0)
        elif self.new_proposals_count:
            new_proposals_count = self.new_proposals_count
        else:
            new_proposals_count = 0
        data["new_proposals_count"] = new_proposals_count
        data["views"] = self["views"]
        data["proposals_count"] = self["proposals_count"]
        if self.get("is_viewed_by_current_user") is not None:
            data["is_viewed_by_current_user"] = self[
                "is_viewed_by_current_user"
            ]
        return data


class JobWithProposalResponse(JobResponse):
    proposals: Optional[List[ProposalIdResponse]] = None
    coauthors: Optional[List[UserSimpleResponse]] = None


class JobFullResponse(JobResponse):
    files: List[FileResponse]


class JobWithProposalFullResponse(JobFullResponse):
    proposals: Optional[List[ProposalResponse]] = None
    coauthors: Optional[List[UserSimpleResponse]] = None


class JobAuthorResponse(JobResponse):
    is_archived: bool
    is_draft: bool
    updated_at: datetime
    proposals_count: Optional[int] = None
    views: Optional[int] = None
    new_proposals_count: Optional[int] = None
    author: Optional[UserSimpleResponse] = None


class JobAuthorFullResponse(JobAuthorResponse, JobFullResponse):
    coauthors: Optional[List[UserSimpleResponse]] = None
