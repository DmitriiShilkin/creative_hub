from sqlalchemy.ext.asyncio import AsyncSession

from crud.city import crud_city
from models.user import UserExperience
from schemas.user.user_experience import ExperienceCreate, ExperienceUpdate
from utilities.queryset import check_found


async def validate_update_data(
    db: AsyncSession, update_data: ExperienceUpdate, experience: UserExperience
) -> None:
    current_model = ExperienceCreate.model_validate(
        experience, from_attributes=True
    )
    updated_model = current_model.model_copy(
        update=update_data.model_dump(exclude_unset=True)
    )
    ExperienceCreate(**updated_model.model_dump())
    if update_data.city_id is not None:
        found_city = await crud_city.get_multi_by_ids(
            db=db, ids=[update_data.city_id]
        )
        await check_found(found_city, [update_data.city_id])
