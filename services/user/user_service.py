import uuid
from datetime import datetime, timedelta, UTC

from sqlalchemy.ext.asyncio import AsyncSession

from constants.user_specialization import VerificationType
from crud.user import crud_user
from crud.verification_code import crud_verification_code
from models.user import User
from schemas.user.user import UserCreate, UserCreateDB, UserUpdate
from security.password import hash_password
from services.timezone import get_timezone_by_tzcode
from services.verify_email import (
    create_email_verification_entry,
    generate_verification_code,
)
from tasks.tasks import send_verif_code_for_verify_email


async def create_user(db: AsyncSession, create_data: UserCreate) -> User:
    try:
        create_data = create_data.model_dump(exclude_unset=True)
        hashed_password = await hash_password(create_data.pop("password"))
        random_uid = str(uuid.uuid4())
        user_created = await crud_user.create(
            db=db,
            create_schema=UserCreateDB(
                uid=random_uid,
                username=random_uid,
                hashed_password=hashed_password,
                **create_data,
                commit=False,
            ),
        )
        verification_code = await generate_verification_code()
        await create_email_verification_entry(
            db,
            user_id=user_created.id,
            verification_code=verification_code,
            verification_type=VerificationType.REGISTRATION,
        )
        await db.flush()

        user_created.contact_info = {"email": user_created.email}
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    send_verif_code_for_verify_email.delay(
        to_email=user_created.email,
        verification_code=verification_code,
    )
    return user_created


async def cancel_email_change(db: AsyncSession, user_id: int) -> None:
    user = await crud_user.get_by_id(db, user_id=user_id)

    if user and user.pending_email:
        user.email = user.pending_email
        user.pending_email = None
        user.is_email_verified = True

        await crud_verification_code.remove(db, obj_id=user_id, commit=False)
        await db.commit()


async def restore_user(
    db: AsyncSession,
    user: User,
) -> None:
    """Восстановление пользователя после удаления в течение 30 дней."""

    one_month_ago = datetime.now(tz=UTC) - timedelta(days=30)
    if user.is_deleted is True and user.deleted_at > one_month_ago:
        user.is_deleted = False
        user.deleted_at = None
        await db.commit()


async def update_user(
    db: AsyncSession, update_schema: UserUpdate, user: User
) -> User:
    try:
        update_data = update_schema.model_dump(exclude_unset=True)

        if "timezone" in update_data and not update_data["timezone"]:
            update_data["timezone_id"] = None

        if update_data.pop("timezone", None):
            found_timezone = await get_timezone_by_tzcode(
                db=db, schema=update_schema.timezone
            )
            update_data["timezone_id"] = found_timezone.id

        updated_user = await crud_user.update(
            db=db, db_obj=user, update_data=update_data, commit=False
        )
        await db.commit()
        await db.refresh(updated_user)
        return updated_user
    except Exception:
        await db.rollback()
        raise
