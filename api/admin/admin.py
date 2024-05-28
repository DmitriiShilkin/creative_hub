from sqladmin import Admin, BaseView, expose
from starlette.requests import Request
from starlette.responses import RedirectResponse

from api.admin.views.calendar.comment import CalendarEventCommentAdmin
from api.admin.views.calendar.event import (
    CalendarEventAdmin,
    CalendarEventUsersAdmin,
)
from api.admin.views.city import CityAdmin, CityTranslationAdmin
from api.admin.views.country import CountryAdmin, CountryTranslationAdmin
from api.admin.views.event import EventAdmin
from api.admin.views.frilance.custom_field import ProposalTableCustomFieldAdmin
from api.admin.views.frilance.job import JobAdmin, JobViewAdmin
from api.admin.views.frilance.proposal import (
    ProposalAdmin,
    ProposalStatusAdmin,
)
from api.admin.views.keyword import KeywordAdmin
from api.admin.views.media_file import MediaFileAdmin
from api.admin.views.organisation.organisation import OrganisationAdmin
from api.admin.views.organisation.organisation_office import (
    OrganisationOfficeAdmin,
)
from api.admin.views.project import (
    ProjectAdmin,
    ProjectCoauthorsAdmin,
    ProjectsKeywordsAdmin,
)
from api.admin.views.text_document import TextDocumentAdmin
from api.admin.views.user.contact_person import ContactPersonAdmin
from api.admin.views.user.direction import (
    DirectionAdmin,
    DirectionTranslationAdmin,
)
from api.admin.views.user.education import EducationAdmin
from api.admin.views.user.favorite import FavoriteAdmin
from api.admin.views.user.link import LinkAdmin
from api.admin.views.user.mentorship import (
    MentorshipAdmin,
    MentorshipDemandAdmin,
    MentorshipTranslationAdmin,
)
from api.admin.views.user.private_site import PrivateSiteAdmin
from api.admin.views.user.social_network import SocialNetworkAdmin
from api.admin.views.user.specialization import (
    SpecializationAdmin,
    SpecializationTranslationAdmin,
)
from api.admin.views.user.user import UserAdmin
from api.admin.views.user.user_experience import UserExperienceAdmin
from api.admin.views.user.user_specialization import (
    UserSpecializationAdmin,
    UserSpecializationTranslationAdmin,
)
from api.admin.views.user.verification_code import VerificationCodeAdmin


class DelimiterAdmin(BaseView):
    name = ""

    @expose("/", methods=["GET"])
    async def test_page(self, request: Request):
        return RedirectResponse("/ch/admin/")


class DelimiterAdmin2(DelimiterAdmin):
    name = " "


class DelimiterAdmin3(DelimiterAdmin):
    name = "  "


def load_admin_site(admin: Admin) -> None:
    admin.add_view(UserAdmin)
    admin.add_view(UserSpecializationAdmin)
    admin.add_view(UserSpecializationTranslationAdmin)
    admin.add_view(UserExperienceAdmin)
    admin.add_view(VerificationCodeAdmin)
    admin.add_view(EducationAdmin)
    admin.add_view(MentorshipAdmin)
    admin.add_view(MentorshipTranslationAdmin)
    admin.add_base_view(DelimiterAdmin2)

    admin.add_view(CityAdmin)
    admin.add_view(CityTranslationAdmin)
    admin.add_view(CountryAdmin)
    admin.add_view(CountryTranslationAdmin)
    admin.add_view(SpecializationAdmin)
    admin.add_view(SpecializationTranslationAdmin)
    admin.add_view(DirectionAdmin)
    admin.add_view(DirectionTranslationAdmin)
    admin.add_view(MentorshipDemandAdmin)
    admin.add_base_view(DelimiterAdmin)

    admin.add_view(JobAdmin)
    admin.add_view(JobViewAdmin)
    admin.add_view(ProposalStatusAdmin)
    admin.add_view(ProposalAdmin)
    admin.add_view(ProposalTableCustomFieldAdmin)
    admin.add_base_view(DelimiterAdmin3)

    admin.add_view(KeywordAdmin)
    admin.add_view(ProjectAdmin)
    admin.add_view(ProjectCoauthorsAdmin)
    admin.add_view(ProjectsKeywordsAdmin)
    admin.add_view(TextDocumentAdmin)
    admin.add_view(FavoriteAdmin)
    admin.add_view(SocialNetworkAdmin)
    admin.add_view(PrivateSiteAdmin)
    admin.add_view(LinkAdmin)
    admin.add_view(EventAdmin)
    admin.add_view(ContactPersonAdmin)
    admin.add_view(OrganisationAdmin)
    admin.add_view(OrganisationOfficeAdmin)
    admin.add_view(MediaFileAdmin)

    admin.add_view(CalendarEventAdmin)
    admin.add_view(CalendarEventUsersAdmin)
    admin.add_view(CalendarEventCommentAdmin)
