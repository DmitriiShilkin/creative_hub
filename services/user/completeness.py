from sqlalchemy.ext.asyncio import AsyncSession

from crud.completeness import crud_completeness
from crud.user import crud_user
from models import User
from schemas.user.user import UserUpdateDB
from schemas.completeness import UserCompleteness

MAIN_FIELDS = (
    "first_name",
    "second_name",
    "username",
    "birthday",
    "timezone",
    "city",
    "languages",
)
SPECIALIZATION_FIELDS = (
    "status",
    "grade",
    "price",
    "specializations",
    "keywords",
)
CONTACTS_FIELDS = (
    "links",
    "email",
    "phone_number",
)
MENTORSHIP_FIELDS = (
    "grades",
    "keywords",
    "demands",
    "specializations",
)


async def calculate_completeness(user: User) -> UserCompleteness:
    main = await check_main_fields(user)
    contacts = await check_contacts_fields(user)
    mentorship = await check_mentorship_fields(user)
    experience = 100 if getattr(user, "experience", None) else 0
    education = 100 if getattr(user, "education", None) else 0
    return UserCompleteness(
        main=main,
        contacts=contacts,
        mentorship=mentorship,
        experience=experience,
        education=education,
    )


async def check_main_fields(user: User) -> int:
    # +1 in total_fields_count = specialization translations description field
    total_fields_count = len(MAIN_FIELDS + SPECIALIZATION_FIELDS) + 1
    not_empty_fields = 0
    for field in MAIN_FIELDS:
        if getattr(user, field, None):
            not_empty_fields += 1

    if getattr(user, "specialization", None):
        for field in SPECIALIZATION_FIELDS:
            if getattr(user.specialization, field, None):
                not_empty_fields += 1

        if getattr(user.specialization, "translations", None):
            for translation in user.specialization.translations:
                if getattr(translation, "description", None):
                    not_empty_fields += 1
                    break

    return round(not_empty_fields * 100 / total_fields_count)


async def check_contacts_fields(user: User) -> int:
    not_empty_fields = 0
    if getattr(user, "links", None):
        not_empty_fields += 1

    if user.contact_info and isinstance(user.contact_info, dict):
        if user.contact_info.get("phone_number"):
            not_empty_fields += 1
        if user.contact_info.get("email"):
            not_empty_fields += 1

    return round(not_empty_fields * 100 / len(CONTACTS_FIELDS))


async def check_mentorship_fields(user: User) -> int:
    # +1 in total_fields_count = mentorship translations description field
    total_fields_count = len(MENTORSHIP_FIELDS) + 1
    not_empty_fields = 0
    if getattr(user, "mentorship", None):
        for field in MENTORSHIP_FIELDS:
            if getattr(user.mentorship, field, None):
                not_empty_fields += 1

        if getattr(user.mentorship, "translations", None):
            for translation in user.mentorship.translations:
                if getattr(translation, "description", None):
                    not_empty_fields += 1
                    break

    return round(not_empty_fields * 100 / total_fields_count)


async def update_user_completeness(db: AsyncSession, user_id: int) -> None:
    update_user = await crud_completeness.get_user_by_id(
        db=db, user_id=user_id
    )
    completeness = await calculate_completeness(update_user)
    update_data = UserUpdateDB(profile_completeness=completeness)
    await crud_user.update(db=db, db_obj=update_user, update_data=update_data)
