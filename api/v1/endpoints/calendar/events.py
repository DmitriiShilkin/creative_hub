from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.dependencies.auth import get_current_user
from api.dependencies.database import get_async_db
from constants.calendar.period import CalendarEventPeriod
from crud.calendar.event import calendar_event_crud
from models.user import User
from schemas.calendar.event import (
    CalendarEventCreate,
    CalendarEventFullResponse,
    CalendarEventResponse,
    CalendarEventUpdate,
)
from services.calendar import event as calendar_event_services

router = APIRouter()


@router.get("/", response_model=List[CalendarEventResponse])
async def read_events_by_period(
    period: CalendarEventPeriod = Query(...),
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    return await calendar_event_services.get_events_by_period(
        db=db, user_id=current_user.id, period=period
    )


@router.get("/{event_id}/", response_model=CalendarEventFullResponse)
async def read_event(
    event_id: int,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    if found_event := await calendar_event_crud.get_by_id_and_user_id(
        db=db, obj_id=event_id, user_id=current_user.id
    ):
        return found_event
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
    )


@router.post(
    "/",
    response_model=CalendarEventResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_event(
    new_event: CalendarEventCreate,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await calendar_event_services.create_event(
            db=db, create_data=new_event, user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.patch("/{event_id}/", response_model=CalendarEventResponse)
async def update_event(
    event_id: int,
    update_data: CalendarEventUpdate,
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
    if found_event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission",
        )
    try:
        return await calendar_event_services.update_event(
            db=db, event=found_event, update_data=update_data
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.delete("/{event_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
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
    if found_event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission",
        )
    await calendar_event_crud.remove(db=db, obj_id=found_event.id)
