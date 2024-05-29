from typing import Optional

from pydantic import BaseModel, PositiveInt

from schemas.link import LinkCreate
from schemas.private_site import PrivateSiteCreate
from schemas.social_network import SocialNetworkCreate
from schemas.user.user_contact_info import ContactInfoCreate


class LinkCreateUpdate(LinkCreate):
    id: Optional[PositiveInt] = None


class SocialNetworksCreateUpdate(SocialNetworkCreate):
    id: Optional[PositiveInt] = None


class UserInfoCreateUpdate(BaseModel):
    links: list[LinkCreateUpdate]
    networks: list[SocialNetworksCreateUpdate]
    contact_info: Optional[ContactInfoCreate]
    private_site: Optional[PrivateSiteCreate] = None
