from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from .views import CompanyViewSet, CompanyMemberViewSet, my_company_member, PartyViewSet, \
    VoteViewSet, MembershipViewSet, InviteViewSet, my_invite

router = routers.DefaultRouter()
router.register(r'company', CompanyViewSet)
router.register(r'company-member', CompanyMemberViewSet)
router.register(r'party', PartyViewSet)
router.register(r'vote', VoteViewSet)
router.register(r'membership', MembershipViewSet)
router.register(r'invite', InviteViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('my-company-member', my_company_member),
    path('my-invite', my_invite),
]