from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from pydantic import BaseModel

from models import (
    User,
    UserSpecialization,
    Mentorship,
    Organisation,
)


class CRUDCompleteness(BaseModel):
    async def get_user_by_id(self, db: AsyncSession, *, user_id: int) -> User:
        statement = (
            select(User)
            .where(
                User.id == user_id,
                User.is_deleted.is_(False),
            )
            .options(
                joinedload(User.city),
                joinedload(User.links),
                joinedload(User.experience),
                joinedload(User.education),
                joinedload(User.timezone),
                joinedload(User.specialization).options(
                    joinedload(UserSpecialization.translations),
                    joinedload(UserSpecialization.keywords),
                    joinedload(UserSpecialization.specializations),
                ),
                joinedload(User.mentorship).options(
                    joinedload(Mentorship.translations),
                    joinedload(Mentorship.keywords),
                    joinedload(Mentorship.specializations),
                    joinedload(Mentorship.demands),
                ),
            )
        )
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_organisation_by_id(
        self, db: AsyncSession, *, orgainsation_id: int
    ) -> Organisation:
        statement = (
            select(Organisation)
            .where(Organisation.id == orgainsation_id)
            .options(
                joinedload(Organisation.city),
                joinedload(Organisation.timezone),
                joinedload(Organisation.keywords),
                joinedload(Organisation.organisation_offices),
                joinedload(Organisation.contact_persons),
                joinedload(Organisation.private_sites),
                joinedload(Organisation.specializations),
            )
        )
        result = await db.execute(statement)
        return result.scalars().first()


crud_completeness = CRUDCompleteness()
