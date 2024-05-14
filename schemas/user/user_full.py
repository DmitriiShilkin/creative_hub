from typing import Optional

from pydantic import Field

from schemas.event import EventResponse
from schemas.link import LinkResponse
from schemas.private_site import PrivateSiteResponse
from schemas.project import ProjectResponse
from schemas.social_network import SocialNetworkResponse
from schemas.user.education import EducationResponse
from schemas.user.user import UserResponse
from schemas.user.user_experience import ExperienceResponse
from schemas.user.user_specialization import UserSpecializationResponse


class UserResponseFull(UserResponse):
    specialization: Optional[UserSpecializationResponse]
    authored_projects: Optional[list[ProjectResponse]] = Field(
        serialization_alias="projects"
    )
    created_events: Optional[list[EventResponse]] = Field(
        serialization_alias="events"
    )
    links: Optional[list[LinkResponse]] = []
    education: Optional[list[EducationResponse]] = []
    experience: Optional[list[ExperienceResponse]] = []
    social_networks: Optional[list[SocialNetworkResponse]] = []
    private_site: Optional[PrivateSiteResponse] = None
