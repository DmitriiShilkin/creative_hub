from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from crud.async_crud import BaseAsyncCRUD
from models import (
    City,
    Education,
    Event,
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
            .options(joinedload(self.model.mentorship))
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
                joinedload(self.model.authored_projects).options(
                    joinedload(Project.coauthors), joinedload(Project.keywords)
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
                joinedload(self.model.specialization)
                .joinedload(UserSpecialization.specializations)
                .joinedload(Specialization.direction),
            )
        )
        result = await db.execute(statement)
        return result.scalars().first()


crud_user = CRUDUser(User)
