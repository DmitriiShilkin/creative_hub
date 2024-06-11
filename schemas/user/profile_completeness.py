from typing import Optional

from pydantic import BaseModel, Field, PositiveInt


class ProfileCompletenessBase(BaseModel):
    main_percentage: int = Field(ge=0, le=100, default=0)
    contacts_percentage: int = Field(ge=0, le=100, default=0)
    education_percentage: int = Field(ge=0, le=100, default=0)
    experience_percentage: int = Field(ge=0, le=100, default=0)
    mentorship_percentage: int = Field(ge=0, le=100, default=0)


class ProfileCompletenessCreate(ProfileCompletenessBase):
    pass


class ProfileCompletenessCreateDB(ProfileCompletenessBase):
    user_id: PositiveInt


class ProfileCompletenessUpdate(ProfileCompletenessBase):
    main_percentage: Optional[int] = Field(ge=0, le=100, default=None)
    contacts_percentage: Optional[int] = Field(ge=0, le=100, default=None)
    education_percentage: Optional[int] = Field(ge=0, le=100, default=None)
    experience_percentage: Optional[int] = Field(ge=0, le=100, default=None)
    mentorship_percentage: Optional[int] = Field(ge=0, le=100, default=None)


class ProfileCompletenessResponse(ProfileCompletenessBase):
    pass
