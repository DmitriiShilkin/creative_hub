from datetime import UTC, datetime
from typing import List, Optional, Self

from fastapi.exceptions import RequestValidationError
from pydantic import (
    BaseModel,
    Field,
    PositiveInt,
    field_validator,
    model_validator,
)

from constants.education import (
    EDUCATION_FINISH_YEAR_MAX,
    EDUCATION_START_YEAR_MIN,
    EducationType,
)
from schemas.city import CityWithCountryResponse
from schemas.common import FileResponse
from schemas.mixins import ParseFromJsonMixin


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
    def validate_dates(self) -> Self:
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
    start_year: int = Field(ge=EDUCATION_START_YEAR_MIN)
    end_month: Optional[int] = Field(ge=1, le=12, default=None)
    end_year: Optional[int] = Field(
        ge=EDUCATION_START_YEAR_MIN, le=EDUCATION_FINISH_YEAR_MAX, default=None
    )
    is_current: bool = False

    class Config:
        from_attributes = True


class EducationCreate(EducationBase, EducationValidationMixin):
    city_id: PositiveInt
    filenames: List[str] = []


class EducationUpdate(EducationBase, EducationValidationMixin):
    city_id: PositiveInt
    filenames: List[str] = []
    education_id: PositiveInt


class EducationCreateMulty(ParseFromJsonMixin):
    educations: List[EducationCreate]


class EducationUpdateMulty(ParseFromJsonMixin):
    educations: List[EducationUpdate]
    files_ids_not_to_delete: List[int] = []


class EducationUpdateSingle(ParseFromJsonMixin):
    type: Optional[EducationType] = None
    name: Optional[str] = None
    department: Optional[str] = None
    start_month: Optional[int] = Field(ge=1, le=12, default=None)
    start_year: Optional[int] = Field(
        ge=EDUCATION_START_YEAR_MIN, default=None
    )
    end_month: Optional[int] = Field(ge=1, le=12, default=None)
    end_year: Optional[int] = Field(
        ge=EDUCATION_START_YEAR_MIN, le=EDUCATION_FINISH_YEAR_MAX, default=None
    )
    is_current: Optional[bool] = False
    city_id: Optional[PositiveInt] = None
    filenames: List[str] = []
    certificates_ids_to_delete: List[PositiveInt] = []


class EducationCreateDB(EducationBase):
    user_id: int
    city_id: int


class EducationUpdateDB(EducationBase):
    type: Optional[EducationType]
    name: Optional[str]
    department: Optional[str]
    start_year: Optional[int]
    start_month: Optional[int]
    id: int
    city_id: int


class EducationResponse(EducationBase):
    id: int
    city: CityWithCountryResponse
    certificates: List[FileResponse]
