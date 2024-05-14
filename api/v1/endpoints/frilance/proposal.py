from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user
from api.dependencies.database import get_async_db
from crud.frilance.job import crud_job
from crud.frilance.proposal import crud_proposal
from crud.frilance.proposal_status import crud_proposal_status
from crud.frilance.proposal_table_config import crud_proposal_table_config
from models import User
from schemas.frilance.proposals import (
    ProposalCreate,
    ProposalCreateDB,
    ProposalFullResponse,
    ProposalResponse,
    ProposalsWithConfigsResponse,
    ProposalUpdateForAuthor,
    ProposalUpdateForSpecialist,
)
from services.frilance import proposal
from utilities.exception import (
    FileNotFound,
    SomeObjectsNotFound,
    WrongAnswerFieldRelation,
)

router = APIRouter()


@router.get(
    "/{job_id}/",
    response_model=ProposalsWithConfigsResponse,
    status_code=status.HTTP_200_OK,
)
async def read_job_proposals(
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
            detail="Job not found.",
        )
    if found_job.Job.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission!",
        )
    proposal_table_config = (
        await crud_proposal_table_config.get_by_job_id_and_user_id(
            db=db, job_id=found_job.Job.id, user_id=current_user.id
        )
    )
    proposals = await crud_proposal.get_multi_by_job_id(db=db, job_id=job_id)
    return {
        "proposals": proposals,
        "configs": proposal_table_config,
    }


@router.post(
    "/{job_id}/",
    response_model=ProposalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_proposal(
    job_id: int,
    files: list[UploadFile],
    create_data: ProposalCreate = Depends(ProposalCreate),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_job = await crud_job.get_by_id(db, obj_id=job_id)
    if not found_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )
    found_proposal = await crud_proposal.get_by_job_id_and_user_id(
        db, job_id=job_id, user_id=current_user.id
    )
    if found_proposal:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Proposal already exist.",
        )

    create_data_db = ProposalCreateDB(
        user_id=current_user.id,
        job_id=job_id,
        **create_data.model_dump(exclude_unset=True)
    )
    return await proposal.create_proposal(
        db=db, files=files, create_data=create_data_db
    )


@router.patch(
    "/{proposal_id}/",
    response_model=ProposalFullResponse,
    status_code=status.HTTP_200_OK,
)
async def update_proposal_for_author(
    proposal_id: int,
    update_data: ProposalUpdateForAuthor,
    files: list[UploadFile] = [],
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_proposal = await crud_proposal.get_by_id_with_job(
        db, obj_id=proposal_id
    )
    if not found_proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )
    if found_proposal.job.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission!",
        )
    if update_data.status_id:
        found_proposal_status = await crud_proposal_status.get_by_id(
            db, obj_id=update_data.status_id
        )
        if not found_proposal_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proposal Status not found",
            )
    try:
        return await proposal.update_proposal_for_author(
            db=db,
            proposal=found_proposal,
            update_data=update_data,
            user_id=current_user.id,
            files=files,
        )
    except (SomeObjectsNotFound, FileNotFound) as ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ex.message
        )
    except WrongAnswerFieldRelation as ex:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=ex.message
        )


@router.put(
    "/{proposal_id}/",
    response_model=ProposalResponse,
    status_code=status.HTTP_200_OK,
)
async def update_proposal_for_specialist(
    proposal_id: int,
    files: list[UploadFile],
    update_data: ProposalUpdateForSpecialist,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_proposal = await crud_proposal.get(db, obj_id=proposal_id)

    if not found_proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )
    if found_proposal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission!",
        )

    return await proposal.update_proposal(
        db=db,
        proposal=found_proposal,
        update_data=update_data,
        files=files,
        user_id=current_user.id,
    )


@router.delete(
    "/{proposal_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_proposal(
    proposal_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_proposal = await crud_proposal.get(db, obj_id=proposal_id)

    if not found_proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )
    if found_proposal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="It's not your proposal!",
        )

    return await crud_proposal.remove(db, obj_id=proposal_id)
