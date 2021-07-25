from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from .views import CompanyMemberViewSet, my_company_member, PartyViewSet, \
    VoteViewSet, MembershipViewSet, InviteViewSet, my_invite, voting, MyInvitedParty
from .views_company import CompanyViewSet, ContractViewSet

router = routers.DefaultRouter()
router.register(r'company', CompanyViewSet)
router.register(r'company-member', CompanyMemberViewSet)
router.register(r'party', PartyViewSet)
router.register(r'vote', VoteViewSet)
router.register(r'membership', MembershipViewSet)
router.register(r'invite', InviteViewSet)
router.register(r'contract', ContractViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('my-company-member', my_company_member),
    path('my-invite', my_invite),
    path('my-party-invite', MyInvitedParty.as_view()),
]