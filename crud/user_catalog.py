from typing import Optional

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Load, joinedload
from sqlalchemy.sql.selectable import Select

from api.filters.user_expert import UserExpertFilter
from api.filters.user_specialist import UserSpecialistFilter
from constants.orm.load_onlys.user import USER_LOAD_ONLY
from constants.orm.load_onlys.user_experience import USER_EXPERIENCE_LOAD_ONLY
from crud.async_crud import BaseAsyncCRUD
from models import (
    City,
    Favorite,
    Keyword,
    Mentorship,
    Project,
    Specialization,
    User,
    UserSpecialization,
)
from models.m2m import (
    MentorshipDemands,
    MentorshipKeywords,
    UserSpecializationKeywords,
    UsersSpecializations,
)
from models.user.mentorship import MentorshipDemand


class CRUDUserCatalog(BaseAsyncCRUD[User, BaseModel, BaseModel]):
    def __init__(self, model):
        super().__init__(model)
        self.specialists_options = (
            Load(self.model).load_only(*USER_LOAD_ONLY),
            joinedload(self.model.authored_projects).joinedload(Project.image),
            joinedload(self.model.mentorship),
            joinedload(self.model.specialization).options(
                joinedload(UserSpecialization.keywords),
                joinedload(UserSpecialization.specializations).joinedload(
                    Specialization.direction
                ),
            ),
            joinedload(self.model.experience).load_only(
                *USER_EXPERIENCE_LOAD_ONLY
            ),
        )
        self.experts_options = (
            Load(self.model).load_only(*USER_LOAD_ONLY),
            joinedload(self.model.mentorship).options(
                joinedload(Mentorship.demands),
                joinedload(Mentorship.keywords),
                joinedload(Mentorship.specializations).joinedload(
                    Specialization.direction
                ),
            ),
            joinedload(self.model.experience).load_only(
                *USER_EXPERIENCE_LOAD_ONLY
            ),
        )

    async def get_specialists(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[UserSpecialistFilter] = None,
    ) -> list[User]:
        statement = await self._get_base_query_for_specialists()
        statement = (
            statement.offset(skip)
            .limit(limit)
            .order_by(self.model.id)
            .options(*self.specialists_options)
            .distinct(self.model.id)
        )
        if filters:
            filtered_statement = filters.filter(statement)
        result = await db.execute(filtered_statement)
        return result.scalars().unique().all()

    async def get_experts(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[UserExpertFilter] = None,
    ) -> list[User]:
        statement = await self._get_base_query_for_experts()
        statement = (
            statement.offset(skip)
            .limit(limit)
            .order_by(self.model.id)
            .options(*self.experts_options)
            .distinct(self.model.id)
        )
        if filters:
            if filters.grades__in:
                statement = statement.filter(
                    Mentorship.grades.overlap(filters.grades__in)
                )
                filters.grades__in = None
            filtered_statement = filters.filter(statement)
        result = await db.execute(filtered_statement)
        return result.scalars().unique().all()

    async def get_specialists_favorite(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[UserSpecialistFilter] = None,
    ) -> list[User]:
        statement = await self._get_base_query_for_specialists()
        statement = (
            statement.join(
                Favorite, Favorite.favorite_user_id == self.model.id
            )
            .filter(Favorite.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(self.model.id)
            .options(*self.specialists_options)
            .distinct(self.model.id)
        )
        if filters:
            filtered_statement = filters.filter(statement)
        result = await db.execute(filtered_statement)
        return result.scalars().unique().all()

    async def get_experts_favorite(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[UserExpertFilter] = None,
    ) -> list[User]:
        statement = await self._get_base_query_for_experts()
        statement = (
            statement.join(
                Favorite, Favorite.favorite_user_id == self.model.id
            )
            .where(Favorite.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(self.model.id)
            .options(*self.experts_options)
            .distinct(self.model.id)
        )
        if filters:
            if filters.grades__in:
                statement = statement.filter(
                    Mentorship.grades.overlap(filters.grades__in)
                )
                filters.grades__in = None
            filtered_statement = filters.filter(statement)
        result = await db.execute(filtered_statement)
        return result.scalars().unique().all()

    async def _get_base_query_for_experts(self) -> Select:
        return (
            select(self.model)
            .join(self.model.mentorship)
            .join(Mentorship.specializations)
            .join(Specialization.direction)
            .outerjoin(
                MentorshipDemands,
                MentorshipDemands.mentorship_id == Mentorship.id,
            )
            .outerjoin(
                MentorshipDemand,
                MentorshipDemand.id == MentorshipDemands.demand_id,
            )
            .outerjoin(
                MentorshipKeywords,
                MentorshipKeywords.mentorship_id == Mentorship.id,
            )
            .outerjoin(Keyword, Keyword.id == MentorshipKeywords.keyword_id)
            .outerjoin(
                City,
                City.id == self.model.city_id,
            )
        )

    async def _get_base_query_for_specialists(self) -> Select:
        return (
            select(self.model)
            .join(
                UserSpecialization, UserSpecialization.user_id == self.model.id
            )
            .outerjoin(
                UsersSpecializations,
                UserSpecialization.id
                == UsersSpecializations.user_specialization_id,
            )
            .outerjoin(
                Specialization,
                UsersSpecializations.specialization_id == Specialization.id,
            )
            .outerjoin(
                UserSpecializationKeywords,
                UserSpecializationKeywords.user_specialization_id
                == UserSpecialization.id,
            )
            .outerjoin(
                Keyword, Keyword.id == UserSpecializationKeywords.keyword_id
            )
            .outerjoin(
                City,
                City.id == self.model.city_id,
            )
        )


crud_user_catalog = CRUDUserCatalog(User)
