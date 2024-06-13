from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import UploadFile as StarletteUploadFile

from api.dependencies.auth import get_current_user
from api.dependencies.database import get_async_db
from crud.city import crud_city
from crud.timezone import crud_timezone
from crud.user import crud_user
from models import User
from schemas.user.user import (
    UserCreate,
    UserDetailResponse,
    UserPhotosResponse,
    UserProfileResponse,
    UserResponse,
    UserSimpleResponse,
    UserUpdate,
)
from schemas.user.user_full import UserResponseFull
from schemas.user.user_info import UserInfoCreateUpdate
from services.user import user_info, user_service
from utilities.exception import SomeObjectsNotFound

router = APIRouter()


@router.get("/profile/", response_model=UserProfileResponse)
async def profile(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get("/{user_uid}/", response_model=UserDetailResponse)
async def read_user(
    user_uid: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    if found_user := await crud_user.get_by_uid(db=db, uid=user_uid):
        return found_user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User {user_uid} not found.",
    )


@router.get("/full/{user_uid}/", response_model=UserResponseFull)
async def read_user_full(
    user_uid: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    if found_user := await crud_user.get_by_uid_full(db=db, uid=user_uid):
        return found_user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User {user_uid} not found.",
    )


@router.post(
    "/",
    response_model=UserSimpleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    create_data: UserCreate,
    db: AsyncSession = Depends(get_async_db),
):
    user = await crud_user.get_by_email(db, email=create_data.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {create_data.email} is already "
            "associated with an account.",
        )
    return await user_service.create_user(db=db, create_data=create_data)


@router.patch("/", response_model=UserResponse)
async def update_user(
    update_data: UserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    if update_data.city_id:
        found_city = await crud_city.get_by_id(
            db=db, obj_id=update_data.city_id
        )
        if not found_city:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"City with id: {update_data.city_id} not found.",
            )
    if update_data.timezone_id:
        found_timezone = await crud_timezone.get_by_id(
            db=db, obj_id=update_data.timezone_id
        )
        if not found_timezone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Timezone with id: "
                f"{update_data.timezone_id} not found.",
            )
    return await crud_user.update(
        db=db, db_obj=current_user, update_data=update_data
    )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    return await crud_user.mark_as_deleted(db=db, user_id=current_user.id)


@router.put(
    "/photos/",
    response_model=UserPhotosResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_photos(
    photo: Optional[UploadFile | str],
    profile_cover: Optional[UploadFile | str],
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    update_data = {}
    if isinstance(photo, StarletteUploadFile):
        update_data["photo"] = photo
    if isinstance(profile_cover, StarletteUploadFile):
        update_data["profile_cover"] = profile_cover

    if isinstance(photo, str):
        if current_user.photo != photo:
            raise HTTPException(status_code=400, detail="Incorrect photo url")
    if isinstance(profile_cover, str):
        if current_user.profile_cover != profile_cover:
            raise HTTPException(
                status_code=400, detail="Incorrect profile_cover url"
            )

    user = await crud_user.update(
        db,
        db_obj=current_user,
        update_data=update_data,
    )
    await db.refresh(user)
    return user


@router.put("/", response_model=UserResponseFull)
async def update_user_info(
    update_data: UserInfoCreateUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await user_info.create_update_user_info(
            db=db, schema=update_data, user_uid=current_user.uid
        )
    except SomeObjectsNotFound as ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ex.message
        )
