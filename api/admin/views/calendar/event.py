from sqladmin import ModelView

from models.calendar.event import CalendarEvent
from models.m2m import CalendarEventUsers


class CalendarEventAdmin(ModelView, model=CalendarEvent):
    name_plural = "Calendar Events"
    page_size = 100
    column_default_sort = ("id", True)
    column_list = [
        CalendarEvent.id,
        CalendarEvent.title,
        CalendarEvent.event_type,
        CalendarEvent.priority,
        CalendarEvent.repeatability,
        CalendarEvent.start_time,
        CalendarEvent.end_time,
        # CalendarEvent.timezone,
        CalendarEvent.created_at,
        CalendarEvent.description,
        CalendarEvent.organizer_id,
        CalendarEvent.organizer,
    ]


class CalendarEventUsersAdmin(ModelView, model=CalendarEventUsers):
    name_plural = "Calendar Event Participants"
    page_size = 100
    column_list = [
        CalendarEventUsers.event_id,
        CalendarEventUsers.user_id,
    ]
