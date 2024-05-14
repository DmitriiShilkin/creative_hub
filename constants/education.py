from enum import StrEnum

EDUCATION_START_YEAR_MIN = 1950


class EducationType(StrEnum):
    HIGHER = "Высшее"
    SECONDARY = "Среднее"
    SECONDARY_SPECIAL = "Среднее специальное"
    POSTGRADUATE = "Послевузовское"
    ADDITIONAL = "Дополнительное"
    PROFESSIONAL = "Профессиональное"
