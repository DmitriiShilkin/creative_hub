from typing import List, Optional, Self
from uuid import UUID

from pydantic import BaseModel, PositiveInt, field_validator, model_validator

from constants.finance import Currency, PaymentPer
from constants.user_specialization import Grade, Status
from schemas.i18n import TranslationBase, TranslationCreate
from schemas.keyword import KeywordCreate, KeywordResponse
from schemas.specialization import SpecializationWithDirectionResponse


class UserSpecializationValidationMixin(BaseModel):
    price: Optional[int] = None
    currency: Optional[Currency] = None
    payment_per: Optional[PaymentPer] = None

    @model_validator(mode="after")
    def validate_payment(self) -> Self:
        if (self.price and self.currency and self.payment_per) or (
            self.price is None
            and self.currency is None
            and self.payment_per is None
        ):
            return self
        else:
            raise ValueError(
                "Fields 'price', 'currency' and 'payment_per' "
                "can only be filled simultaneously."
            )


class UserSpecializationBase(BaseModel):
    grade: Grade
    status: Status
    price: Optional[int] = None
    currency: Optional[Currency] = None
    payment_per: Optional[PaymentPer] = None
    is_ready_to_move: bool
    is_ready_for_remote_work: bool


class UserSpecializationTranslationCreate(TranslationCreate):
    description: Optional[str]


class UserSpecializationCreate(
    UserSpecializationBase,
    UserSpecializationValidationMixin,
):
    specialization_ids: List[PositiveInt] = None
    descriptions: List[UserSpecializationTranslationCreate]
    keywords: List[KeywordCreate]

    @field_validator("descriptions")
    @classmethod
    def validate_descriptions(cls, value):
        languages = {d.lang for d in value}
        if len(languages) != len(value):
            raise ValueError(
                "Found duplicate language data for descriptions field"
            )
        return value


class UserSpecializationCreateDB(UserSpecializationBase):
    user_id: int


class UserSpecializationUpdate(
    UserSpecializationCreate,
    UserSpecializationValidationMixin,
):
    pass


class UserSpecializationUpdateDB(UserSpecializationBase):
    pass


class UserSpecializationTranslationResponse(TranslationBase):
    description: Optional[str]


class UserSpecializationResponse(UserSpecializationBase):
    uid: UUID
    specializations: List[SpecializationWithDirectionResponse]
    keywords: Optional[List[KeywordResponse]]
    translations: Optional[List[UserSpecializationTranslationResponse]]

    class Config:
        from_attributes = True
