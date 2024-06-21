from models import UserExperience

USER_EXPERIENCE_LOAD_ONLY = (
    UserExperience.id,
    UserExperience.start_month,
    UserExperience.start_year,
    UserExperience.end_month,
    UserExperience.end_year,
    UserExperience.still_working,
)
