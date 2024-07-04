from typing import Optional

from pydantic import BaseModel


class FavoriteBase(BaseModel):
    user_id: int
    favorite_user_id: Optional[int]
    organisation_id: Optional[int]
    event_id: Optional[int]
    job_id: Optional[int]
