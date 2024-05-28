import enum

MIN_LENGTH_TITLE = 3
MAX_LENGTH_TITLE = 100
MAX_LENGTH_DESCRIPTION = 1500


class CalendarEventType(enum.StrEnum):
    """
    Тип события:
    - Встреча
    - Важная дата
    - Личное
    - Без категории
    """

    MEETING = "Meeting"
    IMPORTANT_DATE = "Important Date"
    PERSONAL = "Personal"
    NO_CATEGORY = "No Category"


class CalendarEventPriority(enum.StrEnum):
    """
    Приоритет события
    - важное
    - требует внимания
    - без приоритета
    """

    IMPORTANT = "Important"
    REQUIRES_ATTENTION = "Requires Attention"
    WITHOUT_PRIORITY = "Without Priority"


# Пока не реализовано
class CalendarEventRepeatability(enum.StrEnum):
    """
    Повторяемость события
    - каждый день
    - каждую неделю
    - каждый месяц
    - без повторов
    """

    EVERY_DAY = "Every Day"
    EVERY_WEEK = "Every Week"
    EVERY_MONTH = "Every Month"
    NO_REPEATS = "No Repeats"
