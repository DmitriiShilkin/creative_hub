from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from configs.loggers import logger
from crud.frilance.job_views import crud_job_view
from crud.frilance.job_with_counters import crud_job as crud_jwc
from schemas.crud.job import JobDataBaseDTO
from schemas.frilance.job_view import JobViewBase
from utilities.queryset import check_found


async def read_jobs(
    db: AsyncSession,
    jobs_ids: List[int],
    current_user_id: Optional[int],
    current_user_ip: Optional[str],
):
    found_jobs = await crud_jwc.get_multi_by_ids(
        db, ids=jobs_ids, current_user_id=current_user_id, current_user_ip=None
    )
    await check_found(objects=found_jobs, objects_ids=jobs_ids)
    for job in found_jobs:
        await read_job(
            db=db,
            job=job,
            current_user_id=current_user_id,
            current_user_ip=current_user_ip,
        )
    await db.commit()


async def read_job(
    db: AsyncSession,
    job: JobDataBaseDTO,
    current_user_id: Optional[int],
    current_user_ip: Optional[str],
) -> int:
    new_proposals_count = 0

    if not job.existing_view:
        try:
            await crud_job_view.create(
                db,
                create_schema=JobViewBase(
                    job_id=job.Job.id,
                    proposals_views=job.proposals_count,
                    user_id=current_user_id,
                    ip_address=current_user_ip
                    if not current_user_id
                    else None,
                ),
                commit=False,
            )
        except IntegrityError as ex:
            logger.exception(ex)
    elif (
        job.Job.job_views
        and job.Job.job_views[0].proposals_views != job.proposals_count
    ):
        new_proposals_count = (
            job.proposals_count - job.Job.job_views[0].proposals_views
        )
        job.Job.job_views[0].proposals_views = job.proposals_count

    return new_proposals_count
