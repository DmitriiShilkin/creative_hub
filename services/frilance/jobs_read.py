from typing import Optional, Union

from redis import Redis
from redis.asyncio import RedisError
from sqlalchemy.ext.asyncio import AsyncSession

from api.filters.job import JobFilter
from configs.loggers import logger
from crud.frilance.job_with_counters import crud_job as crud_jwc
from schemas.endpoints.paginated_response import (
    JobPaginatedAuthorResponse,
    JobPaginatedResponse,
)
from services.redis import get_browsing_now_by_job


async def read_jobs(
    db: AsyncSession,
    redis: Redis,
    limit: int,
    skip: int,
    current_user_id: Optional[int],
    current_user_ip: Optional[str],
    filters: JobFilter,
    favorite: bool,
) -> JobPaginatedResponse:
    jobs = await crud_jwc.get_multi(
        db,
        limit=limit,
        skip=skip,
        current_user_id=current_user_id,
        current_user_ip=current_user_ip,
        filters=filters,
        favorite=favorite,
    )
    jobs = JobPaginatedResponse.model_validate(jobs, from_attributes=True)
    return await _add_browsing_now(jobs=jobs, redis=redis)


async def read_jobs_for_author(
    db: AsyncSession,
    redis: Redis,
    author_id: int,
    limit: int,
    skip: int,
    filters: JobFilter,
) -> JobPaginatedResponse:
    jobs = await crud_jwc.get_multi_jobs_for_author(
        db, author_id=author_id, filters=filters, limit=limit, skip=skip
    )
    jobs = JobPaginatedAuthorResponse.model_validate(
        jobs, from_attributes=True
    )
    return await _add_browsing_now(jobs=jobs, redis=redis)


async def read_jobs_by_author(
    db: AsyncSession,
    redis: Redis,
    author_id: int,
    limit: int,
    skip: int,
    filters: JobFilter,
    current_user_id: Optional[int],
    current_user_ip: Optional[str],
    favorite: bool,
) -> JobPaginatedResponse:
    jobs = await crud_jwc.get_multi(
        db,
        author_id=author_id,
        limit=limit,
        skip=skip,
        current_user_ip=current_user_ip,
        current_user_id=current_user_id,
        filters=filters,
        favorite=favorite,
    )
    jobs = JobPaginatedResponse.model_validate(jobs, from_attributes=True)
    return await _add_browsing_now(jobs=jobs, redis=redis)


async def _add_browsing_now(
    jobs: Union[JobPaginatedAuthorResponse, JobPaginatedResponse],
    redis: Redis,
) -> Union[JobPaginatedAuthorResponse, JobPaginatedResponse]:
    for job in jobs.objects:
        try:
            count = await get_browsing_now_by_job(redis=redis, job_id=job.id)
            job.browsing_now = count
        except RedisError as ex:
            logger.error(ex)
    return jobs
