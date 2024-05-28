from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import delete, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from crud.async_crud import BaseAsyncCRUD
from models import (
    City,
    Education,
    Event,
    Mentorship,
    Project,
    Specialization,
    User,
    UserExperience,
    UserSpecialization,
)
from schemas.user.user import UserCreateDB, UserUpdate


class CRUDUser(BaseAsyncCRUD[User, UserCreateDB, UserUpdate]):
    async def get_by_id(
        self, db: AsyncSession, *, user_id: int
    ) -> Optional[User]:
        statement = select(self.model).where(self.model.id == user_id)
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_by_email(
        self, db: AsyncSession, *, email: str
    ) -> Optional[User]:
        statement = select(self.model).where(self.model.email == email)
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_by_service_id(
        self,
        db: AsyncSession,
        *,
        service_id_field: str,
        user_service_id: str,
    ) -> Optional[User]:
        statement = select(self.model).where(
            getattr(self.model, service_id_field) == user_service_id
        )
        result = await db.execute(statement)
        return result.scalars().first()

    async def mark_as_deleted(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        commit: bool = True,
    ) -> Optional[User]:
        user = await self.get_by_id(db, user_id=user_id)
        if user:
            user.is_deleted = True
            user.deleted_at = datetime.now(tz=timezone.utc)
            if commit:
                await db.commit()
                await db.refresh(user)
            return user

    async def get_by_uid(
        self, db: AsyncSession, *, uid: UUID
    ) -> Optional[User]:
        statement = (
            select(self.model)
            .where(
                self.model.uid == uid,
                self.model.is_deleted.is_(False),
            )
            .options(
                joinedload(self.model.mentorship),
                joinedload(self.model.contact_info),
                joinedload(self.model.favorites),
                joinedload(self.model.city).joinedload(City.country),
            )
        )
        result = await db.execute(statement)
        return result.scalars().first()

    async def remove_after_30_days(
        self,
        db: AsyncSession,
    ) -> None:
        one_month_ago = datetime.now(tz=timezone.utc) - timedelta(days=30)
        statement = delete(self.model).where(
            self.model.is_deleted.is_(True),
            self.model.deleted_at <= one_month_ago,
        )
        await db.execute(statement)
        await db.commit()

    async def get_by_uid_full(
        self, db: AsyncSession, *, uid: UUID
    ) -> Optional[User]:
        statement = (
            select(self.model)
            .where(
                self.model.uid == uid,
                self.model.is_deleted.is_(False),
            )
            .options(
                joinedload(self.model.city).joinedload(City.country),
                joinedload(self.model.authored_projects).options(
                    joinedload(Project.coauthors), joinedload(Project.keywords)
                ),
                joinedload(self.model.mentorship).options(
                    joinedload(Mentorship.specializations).joinedload(
                        Specialization.direction
                    ),
                    joinedload(Mentorship.translations),
                    joinedload(Mentorship.keywords),
                    joinedload(Mentorship.demands),
                ),
                joinedload(self.model.created_events).options(
                    joinedload(Event.city).joinedload(City.country),
                    joinedload(Event.specializations),
                    joinedload(Event.organizers),
                    joinedload(Event.speakers),
                    joinedload(Event.contact_persons),
                ),
                joinedload(self.model.links),
                joinedload(self.model.education).options(
                    joinedload(Education.city).joinedload(City.country),
                    joinedload(Education.certificates),
                ),
                joinedload(self.model.experience).options(
                    joinedload(UserExperience.city).joinedload(City.country),
                ),
                joinedload(self.model.social_networks),
                joinedload(self.model.private_site),
                joinedload(self.model.specialization).options(
                    joinedload(UserSpecialization.keywords),
                    joinedload(UserSpecialization.specializations).joinedload(
                        Specialization.direction
                    ),
                ),
                joinedload(self.model.contact_info),
            )
        )
        result = await db.execute(statement)
        return result.scalars().first()

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        update_data: Union[UserUpdate, dict],
        commit: bool = True,
    ) -> User:
        if isinstance(update_data, BaseModel):
            update_data = update_data.model_dump(exclude_unset=True)

        stmt = (
            update(self.model)
            .where(self.model.id == db_obj.id)
            .values(**update_data)
            .returning(self.model)
            .options(joinedload(self.model.city).joinedload(City.country))
        )
        result = await db.execute(stmt)
        obj = result.scalars().first()
        if commit:
            await db.commit()
            await db.refresh(obj)
        return obj

    async def get_by_name_or_email(
        self, db: AsyncSession, found_obj: str
    ) -> Optional[User]:
        full_name = self.model.first_name + self.model.second_name
        full_name_swapped = self.model.second_name + self.model.first_name
        statement = select(self.model).where(
            or_(
                self.model.username == found_obj,
                self.model.email == found_obj,
                full_name == found_obj,
                full_name_swapped == found_obj,
            )
        )
        result = await db.execute(statement)
        return result.scalars().first()


crud_user = CRUDUser(User)
