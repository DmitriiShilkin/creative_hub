from typing import Optional

from pydantic import BaseModel, PositiveInt

from schemas.link import LinkCreate
from schemas.private_site import PrivateSiteCreate
from schemas.user.user_contact_info import ContactInfoParsed


class LinkCreateUpdate(LinkCreate):
    id: Optional[PositiveInt] = None


class UserInfoCreateUpdate(BaseModel):
    links: list[LinkCreateUpdate]
    contact_info: Optional[ContactInfoParsed]
    private_site: Optional[PrivateSiteCreate] = None
