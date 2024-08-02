from datetime import datetime, timedelta, UTC
from typing import Optional, Type, Union
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import delete, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, load_only, selectinload

from constants.crud_types import ModelType
from crud.async_crud import BaseAsyncCRUD
from crud.options import city_and_country, user_specialisation, specialisations
from models import (
    City,
    Education,
    Event,
    Mentorship,
    Project,
    User,
    UserExperience,
)
from schemas.user.user import UserCreateDB, UserUpdateDB


class CRUDUser(BaseAsyncCRUD[User, UserCreateDB, UserUpdateDB]):
    def __init__(self, model: Type[ModelType]) -> None:
        super().__init__(model)
        self.full_options = (
            joinedload(self.model.city).options(*city_and_country),
            joinedload(self.model.timezone),
            selectinload(self.model.authored_projects).options(
                selectinload(Project.coauthors),
                selectinload(Project.keywords),
                joinedload(Project.image),
                joinedload(Project.organisation),
                selectinload(Project.specializations).options(
                    *specialisations
                ),
            ),
            joinedload(self.model.mentorship).options(
                selectinload(Mentorship.specializations).options(
                    *specialisations
                ),
                selectinload(Mentorship.translations),
                selectinload(Mentorship.keywords),
                selectinload(Mentorship.demands),
            ),
            selectinload(self.model.created_events).options(
                joinedload(Event.city).joinedload(City.country),
                selectinload(Event.specializations),
                selectinload(Event.organizers),
                selectinload(Event.speakers),
                selectinload(Event.contact_persons),
            ),
            selectinload(self.model.links),
            selectinload(self.model.education).options(
                joinedload(Education.city).joinedload(City.country),
                selectinload(Education.certificates),
            ),
            selectinload(self.model.experience).options(
                joinedload(UserExperience.city).joinedload(City.country),
            ),
            joinedload(self.model.private_site),
            joinedload(self.model.active_organisation),
            user_specialisation,
        )

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
            user.deleted_at = datetime.now(tz=UTC)
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
                joinedload(self.model.favorites),
                joinedload(self.model.city).joinedload(City.country),
            )
        )
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_by_username(
        self, db: AsyncSession, *, username: str
    ) -> Optional[User]:
        statement = (
            select(self.model)
            .where(
                self.model.username == username,
                self.model.is_deleted.is_(False),
            )
            .options(
                joinedload(self.model.mentorship),
                joinedload(self.model.favorites),
                joinedload(self.model.city).joinedload(City.country),
            )
        )
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_by_uid_fast(
        self, db: AsyncSession, *, uid: UUID
    ) -> Optional[User]:
        statement = (
            select(self.model)
            .where(
                self.model.uid == uid,
                self.model.is_deleted.is_(False),
            )
            .options(
                load_only(
                    self.model.id,
                    self.model.uid,
                    self.model.last_visited_at,
                    self.model.main_language,
                )
            )
        )
        result = await db.execute(statement)
        return result.scalars().first()

    async def remove_after_30_days(
        self,
        db: AsyncSession,
    ) -> int:
        one_month_ago = datetime.now(tz=UTC) - timedelta(days=30)
        statement = delete(self.model).where(
            self.model.is_deleted.is_(True),
            self.model.deleted_at <= one_month_ago,
        )
        result = await db.execute(statement)
        await db.commit()
        return result.rowcount

    async def get_by_uid_full(
        self, db: AsyncSession, *, uid: UUID
    ) -> Optional[User]:
        statement = (
            select(self.model)
            .where(
                self.model.uid == uid,
                self.model.is_deleted.is_(False),
            )
            .options(*self.full_options)
        )
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_by_username_full(
        self, db: AsyncSession, *, username: str
    ) -> Optional[User]:
        statement = (
            select(self.model)
            .where(
                self.model.username == username,
                self.model.is_deleted.is_(False),
            )
            .options(*self.full_options)
        )
        result = await db.execute(statement)
        return result.scalars().first()

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        update_data: Union[UserUpdateDB, dict],
        commit: bool = True,
    ) -> User:
        if isinstance(update_data, BaseModel):
            update_data = update_data.model_dump(exclude_unset=True)

        stmt = (
            update(self.model)
            .where(self.model.id == db_obj.id)
            .values(**update_data)
            .returning(self.model)
            .options(
                joinedload(self.model.city).joinedload(City.country),
                joinedload(self.model.timezone),
                joinedload(self.model.active_organisation),
            )
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
