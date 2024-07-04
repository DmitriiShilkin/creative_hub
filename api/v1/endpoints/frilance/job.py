from datetime import datetime, timezone
from typing import Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi_filter import FilterDepends
from pydantic import ValidationError
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user, get_current_user_optional
from api.dependencies.database import get_async_db
from api.dependencies.ip import get_current_user_ip
from api.dependencies.redis import get_redis
from api.filters.job import JobFilter
from crud.frilance.job import crud_job
from crud.frilance.job_with_counters import crud_job as crud_jwc
from crud.user import crud_user
from models import User
from schemas.endpoints.paginated_response import (
    JobPaginatedAuthorResponse,
    JobPaginatedResponse,
)
from schemas.frilance.job import (
    JobAuthorFullResponse,
    JobCreateDraft,
    JobUpdate,
    JobWithProposalFullResponse,
)
from schemas.user.contact_person import ContactPersonAddCreateMulty
from services.frilance import job
from services.frilance import job_view as service_job_view
from services.frilance import jobs_read
from services.redis import add_user_to_browsing_now
from storages.s3_jobs import jobs_storage
from utilities.exception import ObjectNotFound, SomeObjectsNotFound

router = APIRouter()


@router.get(
    "/",
    response_model=JobPaginatedResponse,
    status_code=status.HTTP_200_OK,
)
async def read_jobs(
    filters: JobFilter = FilterDepends(JobFilter),
    db: AsyncSession = Depends(get_async_db),
    limit: int = 20,
    skip: int = 0,
    current_user: Optional[User] = Depends(get_current_user_optional),
    current_user_ip: Optional[str] = Depends(get_current_user_ip),
    redis: Redis = Depends(get_redis),
    favorite: bool = False,
):
    if favorite:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication is required to access favorites",
            )
    current_user_id = current_user.id if current_user else None
    return await jobs_read.read_jobs(
        db,
        limit=limit,
        skip=skip,
        current_user_id=current_user_id,
        current_user_ip=current_user_ip,
        redis=redis,
        filters=filters,
        favorite=favorite,
    )


@router.get(
    "/author/all/",
    response_model=JobPaginatedAuthorResponse,
    status_code=status.HTTP_200_OK,
)
async def read_all_jobs_for_author(
    filters: JobFilter = FilterDepends(JobFilter),
    db: AsyncSession = Depends(get_async_db),
    limit: int = 20,
    skip: int = 0,
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
):
    return await jobs_read.read_jobs_for_author(
        db=db,
        redis=redis,
        limit=limit,
        skip=skip,
        filters=filters,
        author_id=current_user.id,
    )


@router.get(
    "/author/{user_uid}/",
    response_model=JobPaginatedResponse,
    status_code=status.HTTP_200_OK,
)
async def read_author_jobs(
    user_uid: UUID,
    filters: JobFilter = FilterDepends(JobFilter),
    db: AsyncSession = Depends(get_async_db),
    limit: int = 20,
    skip: int = 0,
    current_user: Optional[User] = Depends(get_current_user_optional),
    current_user_ip: Optional[str] = Depends(get_current_user_ip),
    redis: Redis = Depends(get_redis),
    favorite: bool = False,
):
    if favorite:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication is required to access favorites",
            )
    found_user = await crud_user.get_by_uid(db=db, uid=user_uid)
    if not found_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_uid} not found.",
        )

    return await jobs_read.read_jobs_by_author(
        db=db,
        redis=redis,
        author_id=found_user.id,
        limit=limit,
        skip=skip,
        current_user_ip=current_user_ip,
        current_user_id=current_user.id if current_user else None,
        filters=filters,
        favorite=favorite,
    )


@router.get(
    "/{job_id}/",
    response_model=Union[JobWithProposalFullResponse, JobAuthorFullResponse],
    status_code=status.HTTP_200_OK,
)
async def read_job(
    job_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
    current_user_ip: Optional[str] = Depends(get_current_user_ip),
    redis: Redis = Depends(get_redis),
):
    author_id = current_user.id if current_user is not None else None
    found_job = await crud_jwc.get_by_id(
        db, obj_id=job_id, author_id=author_id, current_user_ip=current_user_ip
    )
    if not found_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )
    await add_user_to_browsing_now(
        redis=redis,
        job_id=job_id,
        user_id=current_user.id if current_user else current_user_ip,
    )
    new_proposals_count = await service_job_view.read_job(
        db=db,
        job=found_job,
        current_user_id=author_id,
        current_user_ip=current_user_ip,
    )
    await db.commit()
    if author_id and author_id == found_job.Job.author_id:
        schema_class = JobAuthorFullResponse
    else:
        schema_class = JobWithProposalFullResponse
    return schema_class.model_validate(
        found_job,
        from_attributes=True,
        context={"new_proposals_count": new_proposals_count},
    )


@router.post("/views/")
async def view_jobs(
    jobs_ids: list[int],
    db: AsyncSession = Depends(get_async_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
    current_user_ip: Optional[str] = Depends(get_current_user_ip),
):
    current_user_id = current_user.id if current_user else None
    try:
        await service_job_view.read_jobs(
            db,
            jobs_ids=jobs_ids,
            current_user_id=current_user_id,
            current_user_ip=current_user_ip,
        )
    except SomeObjectsNotFound as ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ex.message
        )


@router.post(
    "/",
    response_model=JobAuthorFullResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_job(
    create_data: JobCreateDraft,
    contact_person_data: ContactPersonAddCreateMulty,
    files: list[UploadFile] = [],
    contact_person_files: list[UploadFile] = [],
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_user = await crud_user.get_by_uid(db=db, uid=create_data.author_uid)
    if not found_user:
        found_user = current_user

    try:
        return await job.create_job(
            db=db,
            user=found_user,
            create_data=create_data,
            files=files,
            specialization_ids=create_data.specialization_ids,
            contact_person_data=contact_person_data,
            contact_person_files=contact_person_files,
        )
    except SomeObjectsNotFound as ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ex.message
        )


@router.post(
    "/copy/{job_id}/",
    response_model=JobAuthorFullResponse,
    status_code=status.HTTP_201_CREATED,
)
async def copy_job(
    job_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    if found_job := await crud_job.get_by_id(
        db, obj_id=job_id, author_id=current_user.id
    ):
        files = await jobs_storage.get_by_names(found_job.filenames)
        specialization_ids = [s.id for s in found_job.specializations]
        create_data = JobCreateDraft(
            specialization_ids=specialization_ids,
            accepted_languages=found_job.accepted_languages,
            budget=found_job.budget,
            currency=found_job.currency,
            payment_per=found_job.payment_per,
            is_negotiable_price=found_job.is_negotiable_price,
            is_draft=found_job.is_draft,
            city_id=found_job.city_id,
            is_remote=found_job.is_remote,
            name=found_job.name,
            description=found_job.description,
            deadline=found_job.deadline,
            adult_content=found_job.adult_content,
            for_verified_users=found_job.for_verified_users,
            author_uid=current_user.uid,
            coauthors_ids=[a.id for a in found_job.coauthors],
        )
        contact_person_data = []
        for person in found_job.contact_persons:
            contact_person_data.append({"contact_person_id": person.id})
        return await job.create_job(
            db=db,
            user=current_user,
            create_data=create_data,
            files=files,
            specialization_ids=specialization_ids,
            contact_person_data=ContactPersonAddCreateMulty(
                data=contact_person_data
            ),
            contact_person_files=[],
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Job not found.",
    )


@router.patch(
    "/{job_id}/",
    response_model=JobAuthorFullResponse,
    status_code=status.HTTP_200_OK,
)
async def update_job(
    job_id: int,
    update_data: JobUpdate,
    contact_person_data: ContactPersonAddCreateMulty,
    files: list[UploadFile] = [],
    contact_person_files: list[UploadFile] = [],
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_job = await crud_job.get_by_id(
        db, obj_id=job_id, author_id=current_user.id
    )

    if not found_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    if found_job.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="It's not your job!",
        )
    try:
        return await job.update_job(
            db=db,
            job=found_job,
            update_data=update_data,
            files=files,
            contact_person_data=contact_person_data,
            contact_person_files=contact_person_files,
        )
    except (SomeObjectsNotFound, ObjectNotFound) as ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ex.message
        )
    except ValidationError as ex:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(ex.errors())
        )


@router.patch(
    "/publish/{job_id}/",
    response_model=JobAuthorFullResponse,
    status_code=status.HTTP_200_OK,
)
async def publish_job(
    job_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_job = await crud_job.get_by_id(
        db, obj_id=job_id, author_id=current_user.id
    )
    if not found_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    if found_job.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="It's not your job!",
        )
    if found_job.is_draft:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot publish a draft job.",
        )
    if not found_job.is_archived:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The job is already published.",
        )
    found_job.is_archived = False
    found_job.published_at = datetime.now(tz=timezone.utc)
    await db.commit()
    await db.refresh(found_job)
    return await crud_jwc.get_by_id(
        db, obj_id=job_id, author_id=current_user.id
    )


@router.patch(
    "/unpublish/{job_id}/",
    response_model=JobAuthorFullResponse,
    status_code=status.HTTP_200_OK,
)
async def unpublish_job(
    job_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_job = await crud_job.get_by_id(
        db, obj_id=job_id, author_id=current_user.id
    )
    if not found_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    if found_job.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="It's not your job!",
        )
    if found_job.is_archived:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The job is not published.",
        )
    found_job.is_archived = True
    await db.commit()
    await db.refresh(found_job)
    return await crud_jwc.get_by_id(
        db, obj_id=job_id, author_id=current_user.id
    )


@router.delete(
    "/{job_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_job(
    job_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_job = await crud_job.get(db, obj_id=job_id)

    if not found_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    if found_job.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="It's not your job!",
        )

    return await crud_job.remove(db, obj_id=job_id)
