from typing import List, Optional

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from constants.event import RegistrationEndType
from crud.city import crud_city
from crud.event import crud_event
from crud.organisation.organisation import crud_organisation
from crud.specialization import crud_specialization
from crud.user import crud_user
from models import Event
from schemas.event import (
    EventCreate,
    EventCreateDB,
    EventCreateDraft,
    EventUpdate,
    EventUpdateDB,
)
from schemas.user.contact_person import ContactPersonAddCreateMulty
from services.timezone import get_timezone_by_tzcode
from services.user.contact_person import add_create_contact_persons
from utilities.queryset import check_found


async def create(
    db: AsyncSession,
    create_data: EventCreateDraft,
    contact_person_data: ContactPersonAddCreateMulty,
    contact_person_files: List[UploadFile],
    user_id: int,
    photo: Optional[UploadFile] = None,
    event_cover: Optional[UploadFile] = None,
) -> Event:
    try:
        if create_data.city_id:
            found_city = await crud_city.get_multi_by_ids(
                db=db, ids=[create_data.city_id]
            )
            await check_found(found_city, [create_data.city_id])

        create_data_dict = create_data.model_dump(exclude_unset=True)
        if create_data.timezone:
            found_timezone = await get_timezone_by_tzcode(
                db=db, schema=create_data.timezone
            )
            create_data_dict["timezone_id"] = found_timezone.id

        if not create_data.is_draft:
            EventCreate.model_validate(obj=create_data_dict)
        if (
            create_data.registration_end_type
            == RegistrationEndType.AT_EVENT_START
        ):
            create_data_dict["registration_end_datetime"] = (
                create_data.start_datetime
            )
        event_create = EventCreateDB(
            **create_data_dict,
            creator_id=user_id,
            photo=photo if photo else None,
            event_cover=event_cover if event_cover else None,
        )
        event = await crud_event.create(
            db=db, create_schema=event_create, commit=False
        )
        if create_data.organizers_uids:
            found_organizers = await crud_user.get_multi_by_uids(
                db=db, uids=create_data.organizers_uids
            )
            await check_found(found_organizers, create_data.organizers_uids)
            event.organizers = found_organizers

        if create_data.speakers_uids:
            found_speakers = await crud_user.get_multi_by_uids(
                db=db, uids=create_data.speakers_uids
            )
            await check_found(found_speakers, create_data.speakers_uids)
            event.speakers = found_speakers
        if create_data.specializations_ids:
            found_specializations = await crud_specialization.get_multi_by_ids(
                db=db, ids=create_data.specializations_ids
            )
            await check_found(
                found_specializations, create_data.specializations_ids
            )
            event.specializations = found_specializations
        if create_data.organisations_ids:
            found_organizations = await crud_organisation.get_multi_by_ids(
                db=db, ids=create_data.organisations_ids
            )
            await check_found(
                found_organizations, create_data.organisations_ids
            )
            event.organisations = found_organizations

        if contact_person_data.data:
            await add_create_contact_persons(
                db=db,
                related_object=event,
                data=contact_person_data.data,
                files=contact_person_files,
            )
        await db.commit()
        return await crud_event.get_by_id_extended(
            db=db, obj_id=event.id, author_id=user_id
        )
    except Exception as ex:
        await db.rollback()
        raise ex


async def update(
    db: AsyncSession,
    event: Event,
    update_data: EventUpdate,
    user_id: int,
    contact_person_data: ContactPersonAddCreateMulty,
    contact_person_files: List[UploadFile],
    photo: Optional[UploadFile] = None,
    event_cover: Optional[UploadFile] = None,
) -> Event:
    try:
        if update_data.city_id:
            found_city = await crud_city.get_multi_by_ids(
                db=db, ids=[update_data.city_id]
            )
            await check_found(found_city, [update_data.city_id])

        update_data_dict = update_data.model_dump(exclude_unset=True)
        if update_data.timezone:
            found_timezone = await get_timezone_by_tzcode(
                db=db, schema=update_data.timezone
            )
            update_data_dict["timezone_id"] = found_timezone.id
        if update_data.is_draft is False:
            if "organizers_uids" not in update_data_dict:
                update_data_dict["organizers_uids"] = [
                    organizer.uid for organizer in event.organizers
                ]
            EventCreate(**{**event.__dict__, **update_data_dict})

        if (
            update_data.registration_end_type
            == RegistrationEndType.AT_EVENT_START
        ):
            update_data_dict["registration_end_datetime"] = (
                update_data.start_datetime
            )

        await crud_event.update(
            db=db,
            db_obj=event,
            update_data=EventUpdateDB(**update_data_dict).model_dump(
                exclude_unset=True
            ),
            commit=False,
        )

        await db.flush(event)

        if isinstance(update_data.organisations_ids, list):
            if update_data.organisations_ids:
                found_organizations = await crud_organisation.get_multi_by_ids(
                    db=db, ids=update_data.organisations_ids
                )
                await check_found(
                    found_organizations, update_data.organisations_ids
                )
                event.organisations = found_organizations
            else:
                event.organisations = []
        if isinstance(update_data.organizers_uids, list):
            if update_data.organizers_uids:
                found_organizers = await crud_user.get_multi_by_uids(
                    db=db, uids=update_data.organizers_uids
                )
                await check_found(
                    found_organizers, update_data.organizers_uids
                )
                event.organizers = found_organizers
            else:
                event.organizers = []
        if isinstance(update_data.speakers_uids, list):
            if update_data.speakers_uids:
                found_speakers = await crud_user.get_multi_by_uids(
                    db=db, uids=update_data.speakers_uids
                )
                await check_found(found_speakers, update_data.speakers_uids)
                event.speakers = found_speakers
            else:
                event.speakers = []
        if isinstance(update_data.specializations_ids, list):
            if update_data.specializations_ids:
                found_specializations = (
                    await crud_specialization.get_multi_by_ids(
                        db=db, ids=update_data.specializations_ids
                    )
                )
                await check_found(
                    found_specializations, update_data.specializations_ids
                )
                event.specializations = found_specializations
            else:
                event.specializations = []

        if photo:
            event.photo = photo
        if event_cover:
            event.event_cover = event_cover

        event.contact_persons = []
        if contact_person_data.data:
            await add_create_contact_persons(
                db=db,
                related_object=event,
                data=contact_person_data.data,
                files=contact_person_files,
            )

        await db.commit()
        await db.refresh(event)
        return await crud_event.get_by_id_extended(
            db, obj_id=event.id, author_id=user_id
        )
    except Exception as ex:
        await db.rollback()
        raise ex
