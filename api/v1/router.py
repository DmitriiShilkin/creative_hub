from fastapi import APIRouter

from api.v1.endpoints.favorite.favorite_user import (
    router as favorite_user_router,
)
from api.v1.endpoints.user.user_experience import (
    router as user_experience_router,
)
from api.v1.endpoints.user.user_specialization import (
    router as user_specialization_router,
)

from .endpoints.auth import router as auth_router
from .endpoints.calendar.comments import router as calendar_comments_router
from .endpoints.calendar.events import router as calendar_events_router
from .endpoints.city import router as city_router
from .endpoints.country import router as country_router
from .endpoints.direction import router as direction_router
from .endpoints.emails.change_email import router as change_email
from .endpoints.emails.vefiry_email import router as email_verify_router
from .endpoints.event import router as event_router
from .endpoints.favorite.favorite_organisation import (
    router as favorite_organisation,
)
from .endpoints.favorite.favorite_user import router as favorite
from .endpoints.frilance.custom_fields.proposal_choice import (
    router as proposal_field_choice_router,
)
from .endpoints.frilance.custom_fields.proposal_field import (
    router as proposal_custom_field_router,
)
from .endpoints.frilance.job import router as job_router
from .endpoints.frilance.proposal import router as proposal_router
from .endpoints.frilance.proposal_status import (
    router as proposal_status_router,
)
from .endpoints.frilance.proposal_table_config import (
    router as proposal_table_config_router,
)
from .endpoints.keyword import router as keyword_router
from .endpoints.link import router as link_router
from .endpoints.organisation.contact_person_organisation import (
    router as contact_person_organisation_router,
)
from .endpoints.organisation.organisation import router as organisation_router
from .endpoints.organisation.organisation_file import (
    router as organisation_file_router,
)
from .endpoints.password.password_change import router as change_password
from .endpoints.password.password_reset import router as reset_password
from .endpoints.private_site import router as private_site_router
from .endpoints.project import router as project_router
from .endpoints.search import router as search_router
from .endpoints.social_network import router as social_network_router
from .endpoints.specialization import router as specialization_router
from .endpoints.text_document import router as text_document_router
from .endpoints.user.contact_person_event import (
    router as contact_person_event_router,
)
from .endpoints.user.contact_person_job import (
    router as contact_person_job_router,
)
from .endpoints.user.education import router as user_education_router
from .endpoints.user.mentorship import router as mentorship_router
from .endpoints.user.user import router as user_router
from .endpoints.user.user_catalogs import router as user_catalogs_router

router = APIRouter(prefix="/v1")

router.include_router(search_router, prefix="/search", tags=["Search"])
router.include_router(user_router, prefix="/user", tags=["User"])
router.include_router(
    user_catalogs_router,
    prefix="",
    tags=["Users Catalog"],
)
router.include_router(auth_router, prefix="", tags=["Auth"])
router.include_router(
    favorite_user_router, prefix="/favorite", tags=["Favorite User"]
)
router.include_router(country_router, prefix="/country", tags=["Location"])
router.include_router(city_router, prefix="/city", tags=["Location"])

router.include_router(
    direction_router, prefix="/direction", tags=["Direction"]
)
router.include_router(
    specialization_router, prefix="/specialization", tags=["Specialization"]
)
router.include_router(
    user_specialization_router,
    prefix="/user-specialization",
    tags=["User Specialization"],
)
router.include_router(
    user_experience_router,
    prefix="/user-experience",
    tags=["User Experience"],
)
router.include_router(
    user_education_router,
    prefix="/user-education",
    tags=["User Education"],
)
router.include_router(
    mentorship_router,
    prefix="/mentorship",
    tags=["Mentorship"],
)
router.include_router(link_router, prefix="/link", tags=["Link"])
router.include_router(
    private_site_router, prefix="/private_site", tags=["Private Site"]
)
router.include_router(
    social_network_router, prefix="/social-network", tags=["Social Network"]
)
router.include_router(
    email_verify_router, prefix="/email-verify", tags=["Email Verify"]
)
router.include_router(
    change_email, prefix="/change-email", tags=["Change Email"]
)
router.include_router(
    reset_password, prefix="/reset-password", tags=["Reset Password"]
)
router.include_router(
    change_password, prefix="/change-password", tags=["Change Password"]
)
router.include_router(project_router, prefix="/project", tags=["Project"])
router.include_router(keyword_router, prefix="/keyword", tags=["Keyword"])

router.include_router(event_router, prefix="/event", tags=["Event"])
router.include_router(
    contact_person_event_router,
    prefix="/contact-person/event",
    tags=["Contact Person Event"],
)
router.include_router(job_router, prefix="/job", tags=["Jobs"])
router.include_router(
    proposal_router, prefix="/job-proposal", tags=["Job Proposals"]
)
router.include_router(
    proposal_table_config_router,
    prefix="/job-proposal/config",
    tags=["Job Proposals Table Config"],
)
router.include_router(
    proposal_custom_field_router,
    prefix="/job-proposal/custom-field",
    tags=["Job Proposal CustomField"],
)
router.include_router(
    proposal_field_choice_router,
    prefix="/job-proposal/custom-field/choice",
    tags=["Job Proposal CustomField Choices"],
)
router.include_router(
    proposal_status_router, prefix="/proposal-status", tags=["Proposal Status"]
)
router.include_router(
    contact_person_job_router,
    prefix="/contact-person/job",
    tags=["Contact Person Job"],
)
router.include_router(
    organisation_router,
    prefix="/organisation",
    tags=["Organisation"],
)
router.include_router(
    organisation_file_router,
    prefix="/organisation-file",
    tags=["Organisation file"],
)
router.include_router(
    contact_person_organisation_router,
    prefix="/contact-person/organisation",
    tags=["Contact Person Organisation"],
)
router.include_router(
    favorite,
    prefix="/favorite-users",
    tags=["Favorite users"],
)
router.include_router(
    favorite_organisation,
    prefix="/favorite-organisations",
    tags=["Favorite organisations"],
)
router.include_router(
    text_document_router,
    prefix="/text-document",
    tags=["Text Document"],
)
router.include_router(
    calendar_events_router,
    prefix="/calendar/event",
    tags=["Calendar Events"],
)
router.include_router(
    calendar_comments_router,
    prefix="/calendar/comment",
    tags=["Calendar Comments"],
)
