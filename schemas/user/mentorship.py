from typing import List, Optional

from pydantic import BaseModel, Field, PositiveInt, field_validator

from constants.finance import Currency, PaymentPer
from constants.user_specialization import Grade
from schemas.i18n import TranslationBase, TranslationCreate
from schemas.keyword import KeywordCreate, KeywordResponse
from schemas.specialization import SpecializationWithDirectionResponse


class MentorshipBase(BaseModel):
    grades: List[Grade]
    is_show: bool
    is_paid: bool
    price: Optional[int] = None
    currency: Optional[Currency] = None
    payment_per: Optional[PaymentPer] = None


class MentorshipTranslationCreate(TranslationCreate):
    description: Optional[str]


class MentorshipTranslationResponse(TranslationBase):
    description: Optional[str]


class MentorshipCreate(MentorshipBase):
    first_is_free: Optional[bool] = False
    demands_ids: List[PositiveInt] = Field(min_length=1)
    specialization_ids: List[PositiveInt]
    keywords: List[KeywordCreate]
    descriptions: List[MentorshipTranslationCreate]

    @field_validator("descriptions")
    @classmethod
    def validate_descriptions(cls, value):
        languages = {d.lang for d in value}
        if len(languages) != len(value):
            raise ValueError(
                "Found duplicate language data for descriptions field"
            )
        return value


class MentorshipCreateDB(MentorshipBase):
    user_id: int


class MentorshipUpdateDB(MentorshipBase):
    first_is_free: bool


class MentorshipUpdate(MentorshipCreate):
    first_is_free: bool


class DemandResponse(BaseModel):
    id: int
    name: str


class MentorshipShortResponse(MentorshipBase):
    keywords: List[KeywordResponse]

    class Config:
        from_attributes = True


class MentorshipWithDemandResponse(MentorshipShortResponse):
    demands: List[DemandResponse]
    first_is_free: bool
    translations: Optional[List[MentorshipTranslationResponse]]
    specializations: List[SpecializationWithDirectionResponse]

    class Config:
        from_attributes = True


class MentorshipResponse(MentorshipShortResponse):
    specializations: List[SpecializationWithDirectionResponse]
    demands: List[DemandResponse]
    first_is_free: bool
    translations: Optional[List[MentorshipTranslationResponse]]

    class Config:
        from_attributes = True
