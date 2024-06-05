from typing import List, Union

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from crud import file_bulk_operations
from crud.city import crud_city
from crud.education import crud_education
from crud.user import crud_user
from models import User
from models.user.education import Education
from models.user.education_file import EducationCertificateFile
from schemas.user.education import (
    EducationCreate,
    EducationCreateDB,
    EducationCreateMulty,
    EducationUpdate,
    EducationUpdateDB,
    EducationUpdateMulty,
    EducationUpdateSingle,
)
from utilities.exception import FileNotFound, ObjectNotFound, PermissionDenied
from utilities.files import get_names_with_files
from utilities.queryset import check_found


async def create_education(
    db: AsyncSession,
    create_data: EducationCreateMulty,
    files: List[UploadFile],
    user: User,
) -> Education:
    try:
        await check_cities(db=db, schemas=create_data.educations)

        create_data_db = []
        filenames = []
        for data in create_data.educations:
            data = data.model_dump()
            filenames.append(data.pop("filenames"))
            create_data_db.append(EducationCreateDB(**data, user_id=user.id))
        new_educations = await crud_education.create_bulk(
            db=db, create_schemas=create_data_db, commit=False
        )
        await db.flush()

        if files:
            await create_certificates(
                db=db,
                files=files,
                educations=new_educations,
                filenames=filenames,
            )

        await db.commit()
        return await crud_education.get_multi_by_ids(
            db=db, ids=[e.id for e in new_educations]
        )
    except Exception as ex:
        await db.rollback()
        raise ex


async def create_certificates(
    db: AsyncSession,
    files: List[UploadFile],
    educations: List[Education],
    filenames: List[str],
) -> None:
    files_with_name = await get_names_with_files(files)
    for education, names in zip(educations, filenames):
        files_to_updload = []
        for name in names:
            if name not in files_with_name.keys():
                raise FileNotFound(f"File with name {name} not found")
            files_to_updload.append(files_with_name[name])
        kwargs = {
            "db": db,
            "model": EducationCertificateFile,
            "entity_column": EducationCertificateFile.education_id,
            "entity_id": education.id,
            "commit": False,
        }
        if files_to_updload:
            created_files = await file_bulk_operations.bulk_create(
                files=files_to_updload, **kwargs
            )
            education.certificates.extend(created_files)


async def update_education_multi(
    db: AsyncSession,
    update_data: EducationUpdateMulty,
    files: List[UploadFile],
    user: User,
) -> Education:
    try:
        user = await crud_user.get_by_uid_full(db=db, uid=user.uid)
        education_ids = {e.education_id for e in update_data.educations}
        found_educations = await crud_education.get_multi_by_ids(
            db=db, ids=education_ids
        )
        await check_found(found_educations, education_ids)
        for education in found_educations:
            if education.user_id != user.id:
                raise PermissionDenied(
                    "You don't have permission to"
                    f" education with id: {education.id}"
                )
        await check_cities(db=db, schemas=update_data.educations)

        update_data_db = []
        filenames = []
        for schema in update_data.educations:
            data = schema.model_dump()
            filenames.append(data.pop("filenames"))
            education_id = data.pop("education_id")
            update_data_db.append(EducationUpdateDB(**data, id=education_id))

        await crud_education.update_bulk(
            db=db, update_schemas=update_data_db, commit=False
        )
        await delete_certificates(
            db=db,
            educations=found_educations,
            exclude_ids=update_data.files_ids_not_to_delete,
        )
        if files:
            await create_certificates(
                db=db,
                files=files,
                educations=found_educations,
                filenames=filenames,
            )
        education_ids_to_delete = [
            e.id for e in user.education if e.id not in education_ids
        ]
        await crud_education.remove_bulk(
            db=db, ids=education_ids_to_delete, commit=False
        )
        await db.commit()
        ids = [e.id for e in found_educations]
        db.expire_all()

        return await crud_education.get_multi_by_ids(db=db, ids=ids)
    except Exception as ex:
        await db.rollback()
        raise ex


async def update_education(
    db: AsyncSession,
    education_id: int,
    update_data: EducationUpdateSingle,
    user: User,
    files: List[UploadFile],
) -> Education:
    try:
        found_education = await crud_education.get_by_id(
            db=db, obj_id=education_id
        )
        if not found_education:
            raise ObjectNotFound(f"Education with id {education_id} not found")
        if found_education.user_id != user.id:
            raise PermissionDenied(
                "You don't have permission to"
                f" education with id: {education_id}"
            )
        if update_data.city_id:
            await check_cities(db=db, schemas=[update_data])
        update_data_dict = update_data.model_dump(
            exclude_unset=True, exclude_none=True
        )
        current_data = EducationCreate.model_validate(obj=found_education)
        EducationCreate(**{**current_data.model_dump(), **update_data_dict})

        filenames = []
        data = update_data.model_dump()
        filenames.append(data.pop("filenames"))
        update_data_db = EducationUpdateDB(**data, id=education_id)

        await crud_education.update(
            db=db,
            db_obj=found_education,
            update_data=update_data_db,
            commit=False,
        )

        kwargs = {
            "db": db,
            "model": EducationCertificateFile,
            "entity_column": EducationCertificateFile.education_id,
            "entity_id": found_education.id,
            "commit": False,
        }
        if update_data.certificates_ids_to_delete:
            found_certificates_ids = {
                certificate.id for certificate in found_education.certificates
            }
            for certificate_id in update_data.certificates_ids_to_delete:
                if certificate_id not in found_certificates_ids:
                    raise ObjectNotFound(
                        f"EducationFile with id {certificate_id} not found"
                    )
            await file_bulk_operations.bulk_delete_by_ids(
                ids=update_data.certificates_ids_to_delete, **kwargs
            )

        if files:
            await create_certificates(
                db=db,
                files=files,
                educations=[found_education],
                filenames=filenames,
            )

        await db.commit()
        db.expire_all()

        return await crud_education.get_by_id(db=db, obj_id=education_id)
    except Exception as ex:
        await db.rollback()
        raise ex


async def check_cities(
    db: AsyncSession, schemas: List[Union[EducationCreate, EducationUpdate]]
) -> None:
    cities_ids = {e.city_id for e in schemas}
    found_cities = await crud_city.get_multi_by_ids(db=db, ids=cities_ids)
    await check_found(found_cities, cities_ids)


async def delete_certificates(
    db: AsyncSession, educations: List[Education], exclude_ids: List[int] = []
) -> None:
    for education in educations:
        kwargs = {
            "db": db,
            "model": EducationCertificateFile,
            "entity_column": EducationCertificateFile.education_id,
            "entity_id": education.id,
            "commit": False,
        }
        await file_bulk_operations.bulk_delete_with_exclude_ids(
            **kwargs, ids=exclude_ids
        )
