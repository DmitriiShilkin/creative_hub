from typing import Generic, Union

from pydantic import BaseModel
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from constants.crud_types import ModelType, UpdateSchemaType


class UpdateAsync(Generic[ModelType, UpdateSchemaType]):
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        update_data: Union[UpdateSchemaType, dict],
        commit: bool = True,
    ) -> ModelType:
        if isinstance(update_data, BaseModel):
            update_data = update_data.model_dump(exclude_unset=True)

        stmt = (
            update(self.model)
            .where(self.model.id == db_obj.id)
            .values(**update_data)
            .returning(self.model)
        )
        res = await db.execute(stmt)
        obj = res.scalars().first()
        if commit:
            await db.commit()
            await db.refresh(obj)
        return obj
