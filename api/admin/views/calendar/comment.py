from sqladmin import ModelView

from models.calendar import CalendarEventComment


class CalendarEventCommentAdmin(ModelView, model=CalendarEventComment):
    name_plural = "Calendar Event Comments"
    page_size = 100
    column_default_sort = ("id", True)
    column_list = [
        CalendarEventComment.id,
        CalendarEventComment.text,
        CalendarEventComment.author_id,
        CalendarEventComment.author,
        CalendarEventComment.event_id,
        CalendarEventComment.event,
    ]
