from typing import List

from pydantic import model_validator

from schemas.project import ProjectSimpleResponse
from schemas.user.mentorship import MentorshipResponse
from schemas.user.user import UserSimpleResponse
from schemas.user.user_experience import ExperienceCatalogResponse
from schemas.user.user_specialization import UserSpecializationResponse


class UserSpecialistResponse(UserSimpleResponse):
    specialization: UserSpecializationResponse
    authored_projects: List[ProjectSimpleResponse]
    experience: List[ExperienceCatalogResponse]
    is_expert: bool

    @model_validator(mode="before")
    def is_expert_validator(self):
        self.is_expert = bool(self.mentorship)
        return self


class UserExpertResponse(UserSimpleResponse):
    mentorship: MentorshipResponse
    experience: List[ExperienceCatalogResponse]
