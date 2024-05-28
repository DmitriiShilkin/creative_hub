from datetime import datetime
from typing import List, Optional, Union

from pytz import utc
from sqlalchemy.ext.asyncio import AsyncSession

from crud.user import crud_user
from models import CalendarEvent, User
from schemas.calendar.event import CalendarEventCreate, CalendarEventUpdate


async def validate_times(
    data: Union[CalendarEventCreate, CalendarEventUpdate],
    event: Optional[CalendarEvent] = None,
) -> None:
    start_time = data.start_time
    end_time = data.end_time
    if start_time and start_time < datetime.now(utc):
        raise ValueError("The start time cannot be earlier than now.")
    if end_time and end_time < datetime.now(utc):
        raise ValueError("The end time cannot be earlier than now.")
    if start_time and end_time and start_time >= end_time:
        raise ValueError(
            "The end time cannot be earlier or equal to start time."
        )
    if event:
        if start_time and end_time is None and start_time >= event.end_time:
            raise ValueError(
                "The start time cannot be later or equal to end time."
            )
        if end_time and start_time is None and event.start_time >= end_time:
            raise ValueError(
                "The end time cannot be earlier or equal to start time."
            )


async def check_participants(
    db: AsyncSession, user_id: int, participants: List[str]
) -> List[User]:
    checked_participants = []
    for participant in participants:
        participant = await crud_user.get_by_name_or_email(
            db=db, found_obj=participant
        )
        if participant is None:
            raise ValueError("User not found")
        if participant.id == user_id:
            raise ValueError("You can't be a participant you are an organizer")
        if participant in checked_participants:
            raise ValueError(
                f"The participant {participant.username} has already been "
                f"added in event"
            )
        checked_participants.append(participant)
    return checked_participants
