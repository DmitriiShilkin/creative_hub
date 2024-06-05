from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user
from api.dependencies.database import get_async_db
from crud.education import crud_education
from crud.user import crud_user
from models import User
from schemas.user.education import (
    EducationCreateMulty,
    EducationResponse,
    EducationUpdateMulty,
    EducationUpdateSingle,
)
from services.user import education
from utilities.exception import (
    FileNotFound,
    ObjectNotFound,
    PermissionDenied,
    SomeObjectsNotFound,
)

router = APIRouter()


@router.get("/{user_uid}/", response_model=List[EducationResponse])
async def read_user_education(
    user_uid: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    found_user = await crud_user.get_by_uid(db, uid=user_uid)
    if not found_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with uid {user_uid} not found.",
        )
    return await crud_education.get_multi_by_user_id(db, user_id=found_user.id)


@router.post(
    "/",
    response_model=List[EducationResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_user_education(
    create_data: EducationCreateMulty,
    files: List[UploadFile] = [],
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await education.create_education(
            db=db, create_data=create_data, files=files, user=current_user
        )
    except (SomeObjectsNotFound, FileNotFound) as ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ex.message
        )


@router.put(
    "/",
    response_model=List[EducationResponse],
    status_code=status.HTTP_200_OK,
)
async def update_education_multi(
    update_data: EducationUpdateMulty,
    files: List[UploadFile] = [],
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await education.update_education_multi(
            db=db, update_data=update_data, files=files, user=current_user
        )
    except (SomeObjectsNotFound, FileNotFound) as ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ex.message
        )
    except PermissionDenied as ex:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ex.message,
        )


@router.patch(
    "/{education_id}/",
    response_model=EducationResponse,
    status_code=status.HTTP_200_OK,
)
async def update_education(
    education_id: int,
    update_data: EducationUpdateSingle,
    files: List[UploadFile] = [],
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await education.update_education(
            db=db,
            education_id=education_id,
            update_data=update_data,
            files=files,
            user=current_user,
        )
    except (SomeObjectsNotFound, FileNotFound, ObjectNotFound) as ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ex.message
        )
    except PermissionDenied as ex:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ex.message,
        )
    except RequestValidationError as ex:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(ex.errors())
        )


@router.delete("/{education_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_education(
    education_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_education = await crud_education.get_by_id(db, obj_id=education_id)
    if not found_education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education record not found.",
        )
    if found_education.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission!",
        )
    await crud_education.remove(db, obj_id=education_id)
