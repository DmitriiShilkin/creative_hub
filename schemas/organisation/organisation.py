from datetime import datetime
import json
from typing import Any, List, Optional, Self

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, PositiveInt, field_serializer, model_validator

from schemas.city import CityWithCountryResponse, CityResponse
from schemas.common import UIDResponse
from schemas.i18n import TranslationBase, ValidatedLanguage
from schemas.keyword import KeywordCreate, KeywordResponse
from schemas.media_file import MediaFileResponse
from schemas.organisation.organisation_office import OrganisationOfficeResponse
from schemas.private_site import PrivateSiteResponse
from schemas.specialization import SpecializationWithDirectionResponse
from schemas.timezone import TimezoneCreate, TimezoneResponse
from schemas.user.contact_person import ContactPersonResponse
from schemas.user.user import UserSimpleResponse
from schemas.user.user_contact_info import ContactInfoParsed
from schemas.user.user_specialization import DescriptionTranslationCreate
from schemas.completeness import (
    OrganisationCompleteness,
    OrganisationCompletenessResponse,
)


class OrganisationBase(BaseModel):
    name: str
    communication_languages: List[ValidatedLanguage]
    slug: str
    employee_count_from: Optional[int] = None
    employee_count_to: Optional[int] = None
    exact_employee_count: Optional[int] = None
    use_exact_employee_count: Optional[bool] = None
    legal_address: Optional[str] = None

    class Config:
        from_attributes = True


class OrganizationTranslation(DescriptionTranslationCreate):
    short_info: Optional[str]


class OrganizationTranslationResponse(TranslationBase):
    short_info: Optional[str]
    description: Optional[str]


class OrganisationCreate(OrganisationBase):
    timezone: TimezoneCreate
    specializations_ids: List[PositiveInt]
    use_exact_employee_count: bool = False
    keywords: List[KeywordCreate]
    city_id: Optional[PositiveInt] = None
    translations: List[OrganizationTranslation]

    @model_validator(mode="after")
    def validate_employee_count(self, data: Any) -> Self:
        employee_count_from = self.employee_count_from
        employee_count_to = self.employee_count_to
        exact_employee_count = self.exact_employee_count
        use_exact_employee_count = self.use_exact_employee_count

        if (
            employee_count_from is not None
            and employee_count_to is not None
            and employee_count_from > employee_count_to
        ):
            err = (
                "`exact_employee_count` must be less than"
                "`employee_count_to`."
            )
            raise RequestValidationError(err)

        if use_exact_employee_count:
            if exact_employee_count is None:
                err = (
                    "`exact_employee_count` must be specified when "
                    "`use_exact_employee_count` is `True`."
                )
                raise RequestValidationError(err)
            if (
                employee_count_from is not None
                or employee_count_to is not None
            ):
                err = (
                    "When `use_exact_employee_count` is `True`, "
                    "`employee_count_from` and `employee_count_to`"
                    "must be `None`."
                )
                raise RequestValidationError(err)
        elif exact_employee_count is not None:
            err = (
                "`exact_employee_count` must be `None` when"
                "`use_exact_employee_count` is `False`."
            )
            raise RequestValidationError(err)
        return self

    class Config:
        from_attributes = True


class OrganisationCreateDB(OrganisationBase):
    creator_id: int
    city_id: Optional[PositiveInt] = None
    timezone_id: Optional[PositiveInt] = None

    class Config:
        from_attributes = True


class OrganisationUpdate(OrganisationCreate):
    sections: Optional[List[str]] = None


class OrganisationUpdateDB(OrganisationBase):
    name: Optional[str] = None
    description: Optional[str] = None
    communication_language: Optional[ValidatedLanguage] = None
    employee_count_from: Optional[int] = None
    employee_count_to: Optional[int] = None
    exact_employee_count: Optional[int] = None
    use_exact_employee_count: Optional[bool] = None
    legal_address: Optional[str] = None
    city_id: Optional[PositiveInt] = None
    timezone_id: Optional[PositiveInt] = None
    sections: Optional[List[str]] = None


class OrganisationSimpleResponse(OrganisationBase):
    id: int
    photo: Optional[str] = None
    organisation_cover: Optional[str] = None
    created_at: datetime
    translations: List[OrganizationTranslationResponse]
    creator: UserSimpleResponse
    contact_info: Optional[ContactInfoParsed]
    city: Optional[CityWithCountryResponse]


class OrganisationCatalogResponse(BaseModel):
    id: int
    name: str
    communication_languages: List[ValidatedLanguage]
    photo: Optional[str] = None
    translations: List[OrganizationTranslationResponse]
    creator: UIDResponse
    contact_info: Optional[ContactInfoParsed]
    city: Optional[CityResponse]
    private_sites: List[PrivateSiteResponse]


class UserOrganisationsResponse(OrganisationCatalogResponse):
    is_active: Optional[bool] = False
    slug: str


class OrganisationResponse(OrganisationSimpleResponse):
    specializations: List[SpecializationWithDirectionResponse]
    keywords: List[KeywordResponse]
    timezone: TimezoneResponse
    organisation_offices: List[OrganisationOfficeResponse]
    files: List[MediaFileResponse]
    private_sites: List[PrivateSiteResponse]
    contact_persons: List[ContactPersonResponse]
    sections: Optional[List[str]] = None
    profile_completeness: OrganisationCompletenessResponse


class OrganisationFavoriteResponse(BaseModel):
    id: int
    name: str
    photo: Optional[str] = None
    translations: List[OrganizationTranslationResponse]


class OrganisationShortResponse(BaseModel):
    id: int
    name: str
    photo: Optional[str] = None
    private_sites: List[PrivateSiteResponse]
    translations: List[OrganizationTranslationResponse]


class OrganisationPhotos(BaseModel):
    photo: Optional[str] = None
    organisation_cover: Optional[str] = None


class OrganisationCompletenessUpdateDB(BaseModel):
    profile_completeness: Optional[OrganisationCompleteness] = None

    @field_serializer("profile_completeness")
    def serialize_to_json(completeness: OrganisationCompleteness) -> str:
        return json.dumps(completeness.__dict__)
