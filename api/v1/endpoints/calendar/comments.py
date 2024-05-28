from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies.auth import get_current_user
from api.dependencies.database import get_async_db
from crud.calendar.comment import calendar_comments_crud
from crud.calendar.event import calendar_event_crud
from models.user import User
from schemas.calendar.comments import (
    CommentCreate,
    CommentCreateDB,
    CommentResponse,
    CommentResponseBase,
    CommentUpdate,
)

router = APIRouter()


@router.get("/event/{event_id}/", response_model=List[CommentResponse])
async def read_event_comments(
    event_id: int,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    if found_event := await calendar_event_crud.get_by_id_and_user_id(
        db=db, user_id=current_user.id, obj_id=event_id
    ):
        return await calendar_comments_crud.get_multi_by_event_id(
            db=db, event_id=found_event.id
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
    )


@router.get("/{comment_id}/", response_model=CommentResponse)
async def read_event_comment(
    comment_id: int,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    if found_comment := await calendar_comments_crud.get_by_id(
        db=db,
        obj_id=comment_id,
    ):
        return found_comment
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
    )


@router.post(
    "/{event_id}/",
    response_model=CommentResponseBase,
    status_code=status.HTTP_201_CREATED,
)
async def create_event_comment(
    event_id: int,
    new_comment: CommentCreate,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_event = await calendar_event_crud.get_by_id_and_user_id(
        db=db, obj_id=event_id, user_id=current_user.id
    )
    if not found_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    comment_data = CommentCreateDB(
        author_id=current_user.id,
        event_id=found_event.id,
        **new_comment.model_dump(),
    )
    return await calendar_comments_crud.create(
        db=db, create_schema=comment_data
    )


@router.patch("/{comment_id}/", response_model=CommentResponseBase)
async def update_event_comment(
    comment_id: int,
    update_data: CommentUpdate,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_comment = await calendar_comments_crud.get_by_id(
        db=db, obj_id=comment_id
    )
    if not found_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    if found_comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission",
        )
    return await calendar_comments_crud.update(
        db=db, db_obj=found_comment, update_data=update_data
    )


@router.delete("/{comment_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event_comment(
    comment_id: int,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    found_comment = await calendar_comments_crud.get_by_id(
        db=db, obj_id=comment_id
    )
    if not found_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    if found_comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission",
        )
    return await calendar_comments_crud.remove(db=db, obj_id=found_comment.id)
