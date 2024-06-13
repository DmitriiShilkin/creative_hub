from typing import Optional

from pydantic import Field

from schemas.event import EventSimpleResponse
from schemas.link import LinkResponse
from schemas.private_site import PrivateSiteResponse
from schemas.project import ProjectResponse
from schemas.social_network import SocialNetworkResponse
from schemas.timezone import TimezoneResponse
from schemas.user.education import EducationResponse
from schemas.user.mentorship import MentorshipWithDemandResponse
from schemas.user.user import UserResponse
from schemas.user.user_contact_info import ContactInfoResponse
from schemas.user.user_experience import ExperienceResponse
from schemas.user.user_specialization import UserSpecializationResponse


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
    social_networks: list[SocialNetworkResponse]
    private_site: Optional[PrivateSiteResponse] = None
    mentorship: Optional[MentorshipWithDemandResponse] = None
    contact_info: Optional[ContactInfoResponse] = None
    timezone: Optional[TimezoneResponse] = None
