from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from api.dependencies.auth import get_current_user
from api.dependencies.database import get_async_db
from constants.user.contact_person import (
    CREATE_DATA_EXAMPLE,
    UPDATE_DATA_EXAMPLE,
)
from crud.frilance.job import crud_job
from models import User
from schemas.user.contact_person import ContactPersonResponse
from services.dto import contact_person as contact_person_dto
from services.dto.exception import DTOException
from services.user import contact_person
from utilities.exception import SomeObjectsNotFound

router = APIRouter()


@router.post(
    "/{job_id}/",
    response_model=list[ContactPersonResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(
    job_id: int,
    files: list[UploadFile] = File([]),
    contacts_data: str = Form(examples=[CREATE_DATA_EXAMPLE]),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_job = await crud_job.get_by_id(
        db, obj_id=job_id, author_id=current_user.id
    )
    if not found_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )

    try:
        contacts_data_schemas = await contact_person_dto.to_create_schemas(
            files=files, contacts_data=contacts_data
        )
    except DTOException as ex:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ex.message,
        )
    else:
        return await contact_person.create_contact_persons(
            db,
            contacts_data_schemas=contacts_data_schemas,
            related_object=found_job.Job,
        )


@router.patch(
    "/{job_id}/",
    status_code=status.HTTP_200_OK,
    response_model=list[ContactPersonResponse],
)
async def update_contact(
    job_id: int,
    contacts_data: str = Form(examples=[UPDATE_DATA_EXAMPLE]),
    files: list[UploadFile] = File([]),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_job = await crud_job.get_by_id(
        db, obj_id=job_id, author_id=current_user.id
    )
    if not found_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )

    try:
        contacts_data_schemas = await contact_person_dto.to_update_schemas(
            files=files, contacts_data=contacts_data
        )
    except DTOException as ex:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ex.message,
        )
    else:
        await contact_person.update_contact_persons(
            db, contacts_data_schemas=contacts_data_schemas
        )
        await db.refresh(found_job.Job)
        return found_job.Job.contact_persons


@router.delete(
    "/{job_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_contact(
    job_id: int,
    contact_person_ids: list[int],
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_job = await crud_job.get_by_id(
        db, obj_id=job_id, author_id=current_user.id
    )
    if not found_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )

    try:
        await contact_person.remove_contact_persons(
            db,
            related_object=found_job.Job,
            contact_person_ids=contact_person_ids,
        )
    except SomeObjectsNotFound as ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ex.message,
        )
