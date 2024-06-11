from crud.async_crud import BaseAsyncCRUD
from models import ProfileCompleteness
from schemas.user.profile_completeness import (
    ProfileCompletenessCreateDB,
    ProfileCompletenessUpdate,
)


class CRUDUserProfileCompleteness(
    BaseAsyncCRUD[
        ProfileCompleteness,
        ProfileCompletenessCreateDB,
        ProfileCompletenessUpdate,
    ]
):
    ...


crud_profile_completeness = CRUDUserProfileCompleteness(ProfileCompleteness)
