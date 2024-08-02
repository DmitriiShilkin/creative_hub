from typing import Optional

from pydantic import Field

from schemas.event import EventSimpleResponse
from schemas.link import LinkResponse
from schemas.private_site import PrivateSiteResponse
from schemas.project import ProjectResponse
from schemas.timezone import TimezoneResponse
from schemas.user.education import EducationResponse
from schemas.user.mentorship import MentorshipWithDemandResponse
from schemas.user.user import UserResponse
from schemas.user.user_contact_info import ContactInfoParsed
from schemas.user.user_experience import ExperienceResponse
from schemas.user.user_specialization import UserSpecializationResponse
from schemas.completeness import UserCompletenessResponse


class UserResponseFull(UserResponse):
    specialization: Optional[UserSpecializationResponse]
    authored_projects: Optional[list[ProjectResponse]] = Field(
        serialization_alias="projects"
    )
    created_events: Optional[list[EventSimpleResponse]] = Field(
        serialization_alias="events"
    )
    links: list[LinkResponse]
    education: list[EducationResponse]
    experience: list[ExperienceResponse]
    private_site: Optional[PrivateSiteResponse] = None
    mentorship: Optional[MentorshipWithDemandResponse] = None
    contact_info: Optional[ContactInfoParsed]
    timezone: Optional[TimezoneResponse] = None
    profile_completeness: UserCompletenessResponse
