from typing import Generic, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from constants.crud_types import ModelType


class DeleteAsync(Generic[ModelType]):
    async def remove(
        self, db: AsyncSession, *, obj_id: int, commit: bool = True
    ) -> Optional[ModelType]:
        obj = await db.get(self.model, obj_id)
        if not obj:
            return None

        await db.delete(obj)
        if commit:
            await db.commit()
        return obj
