from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from .views_company import CompanyViewSet, ContractViewSet, InviteViewSet
from .views_party import PartyViewSet, MembershipViewSet, VoteViewSet
from .views_team import TeamMemberViewSet, TeamViewSet, upload_team_image, delete_team_image, \
    upload_team_member_image, delete_team_member_image

router = routers.DefaultRouter()
router.register(r'company', CompanyViewSet)
router.register(r'party', PartyViewSet)
router.register(r'vote', VoteViewSet)
router.register(r'membership', MembershipViewSet)
router.register(r'invite', InviteViewSet)
router.register(r'contract', ContractViewSet)
router.register(r'team', TeamViewSet)
router.register(r'member', TeamMemberViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('upload-team-image/', upload_team_image),
    path('delete-team-image/<int:pk>/', delete_team_image),
    path('upload-team-member-image/', upload_team_member_image),
    path('delete-team-member-image/<int:pk>/', delete_team_member_image)
]