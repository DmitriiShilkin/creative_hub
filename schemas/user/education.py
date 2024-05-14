from datetime import UTC, datetime
from typing import Optional
from uuid import UUID

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator, model_validator

from constants.education import EDUCATION_START_YEAR_MIN, EducationType
from schemas.city import CityWithCountryResponse
from schemas.common import FileResponse
from utilities.decorators import as_form


class EducationValidationMixin(BaseModel):
    start_year: int
    start_month: int
    end_year: Optional[int] = None
    end_month: Optional[int] = None
    is_current: bool = False

    @field_validator("start_year")
    @classmethod
    def validate_start_year(cls, value: int) -> int:
        if value < EDUCATION_START_YEAR_MIN:
            raise RequestValidationError(
                f"The start year of study cannot be less than "
                f"{EDUCATION_START_YEAR_MIN}."
            )
        return value

    @field_validator("end_year")
    @classmethod
    def validate_end_year(cls, value: int) -> Optional[int]:
        year_now: int = datetime.now(UTC).year
        if value is not None and value > year_now:
            raise RequestValidationError(
                "The year of graduation cannot exceed the current year."
            )
        return value

    @model_validator(mode="after")
    def validate_dates(self) -> "EducationCreate":
        if (self.end_year or self.end_month) and self.is_current:
            raise RequestValidationError(
                "You cannot specify the `end_year` or `end_month` "
                "and `is_current` at the same time."
            )
        if (not self.is_current or self.end_year) and self.end_month is None:
            raise RequestValidationError(
                "Value of `end_month` cannot be empty if "
                "`end_year` is filled or `is_current` is not."
            )
        if (not self.is_current or self.end_month) and self.end_year is None:
            raise RequestValidationError(
                "Value of `end_year` cannot be empty if "
                "`end_month` is filled or `is_current` is not."
            )

        if not self.is_current:
            if self.end_year < self.start_year:
                raise RequestValidationError(
                    "The year of graduation precedes the start year."
                )

            if (
                self.end_year == self.start_year
                and self.end_month < self.start_month
            ):
                raise RequestValidationError(
                    "The month of graduation precedes the start month."
                )

        return self


class EducationBase(BaseModel):
    type: EducationType
    name: str
    department: str
    start_month: int = Field(ge=1, le=12)
    start_year: int
    end_month: Optional[int] = Field(ge=1, le=12, default=None)
    end_year: Optional[int] = None
    is_current: bool = False

    class Config:
        from_attributes = True


@as_form
class EducationCreate(EducationBase, EducationValidationMixin):
    city_id: int
    user_uid: UUID


@as_form
class EducationUpdate(EducationBase, EducationValidationMixin):
    city_id: int


class EducationCreateDB(EducationBase):
    user_id: int
    city_id: int


class EducationResponse(EducationBase):
    id: int
    city: CityWithCountryResponse
    certificates: list[FileResponse]
