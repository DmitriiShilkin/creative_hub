from datetime import UTC, datetime
from typing import Optional

from pydantic import (
    BaseModel,
    Field,
    PositiveInt,
    field_validator,
    model_validator,
)

from constants.user.user_experience import EXPERIENCE_START_YEAR_MIN
from schemas.city import CityWithCountryResponse


class ExperienceBase(BaseModel):
    company_name: str
    job_title: str
    start_month: int = Field(ge=1, le=12)
    start_year: int
    end_month: Optional[int] = Field(ge=1, le=12, default=None)
    end_year: Optional[int] = None
    still_working: bool = False


class ExperienceCreate(ExperienceBase):
    city_id: int

    @field_validator("start_year")
    @classmethod
    def validate_start_year(cls, value: int) -> int:
        if value < EXPERIENCE_START_YEAR_MIN:
            raise ValueError(
                f"The 'start_year' cannot be less than"
                f"{EXPERIENCE_START_YEAR_MIN}."
            )
        return value

    @field_validator("end_year")
    @classmethod
    def validate_end_year(cls, value: int) -> Optional[int]:
        year_now: int = datetime.now(UTC).year
        if value is not None and value > year_now:
            raise ValueError("The 'end_year' cannot exceed the current year.")
        return value

    @model_validator(mode="after")
    def validate_dates(self) -> "ExperienceCreate":
        if not self.still_working and not self.end_month and not self.end_year:
            raise ValueError(
                "You should specify 'still_working' or 'end_year, end_month'."
            )
        elif not self.still_working and (
            not self.end_month or not self.end_year
        ):
            raise ValueError(
                "Both values for 'end_month', 'end_year' should be set."
            )
        elif self.still_working and (self.end_month or self.end_year):
            raise ValueError(
                "You should specify only 'still_working' or"
                " 'end_year, end_month'"
            )

        if not self.still_working:
            if self.end_year < self.start_year:
                raise ValueError("The end year is earlier than start year.")
            elif (
                self.end_year == self.start_year
                and self.end_month < self.start_month
            ):
                raise ValueError("The end month is earlier than start month.")
        return self


class ExperienceCreateDB(ExperienceCreate):
    user_id: int


class ExperienceUpdate(BaseModel):
    company_name: Optional[str] = None
    city_id: Optional[int] = None
    job_title: Optional[str] = None
    start_month: Optional[int] = None
    start_year: Optional[int] = None
    end_month: Optional[int] = None
    end_year: Optional[int] = None
    still_working: Optional[bool] = None


class ExperienceResponse(ExperienceBase):
    id: int
    city: CityWithCountryResponse


class ExperienceCatalogResponse(BaseModel):
    id: PositiveInt
    start_month: int
    start_year: int
    end_month: Optional[int]
    end_year: Optional[int]
    still_working: bool
